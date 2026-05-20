from contextlib import asynccontextmanager

import librosa
from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from app.classification.clap_audio_model import ClapAudioModel
from app.classification.classifier import MusicClassifier
from app.classification.labels import SOUNDBOARD_LABELS
from app.config import API_TOKEN, MAX_UPLOAD_SIZE, SAMPLE_RATE
from app.upload.audio_feature_extractor import AudioFeatureExtractor
from app.upload.temp_upload_file_manager import TempUploadFileManager
from app.upload.upload_validator import UploadValidator


# ---------------------------------------------------------------------------
# Model holder (loaded once at startup)
# ---------------------------------------------------------------------------
audio_model: ClapAudioModel | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global audio_model
    audio_model = ClapAudioModel()
    yield


app = FastAPI(
    title="Music Labeler",
    description="Microservice IA local pour labeliser les musiques (CLAP zero-shot). "
                "Stateless : le fichier uploadé est analysé puis supprimé, rien n'est conservé.",
    version="1.0.0",
    lifespan=lifespan,
)


def _verify_token(request: Request) -> None:
    """Vérifie le token API dans le header Authorization."""
    if not API_TOKEN:
        return  # Pas de token configuré = pas de vérification (dev local)
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer ") or auth_header[7:] != API_TOKEN:
        raise HTTPException(status_code=401, detail="Token invalide ou manquant")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/label", dependencies=[Depends(_verify_token)])
async def label_upload(
    file: UploadFile = File(...),
    top_k: int = Query(default=3, ge=1, le=10),
):
    
    """Labelise un fichier audio uploadé. Le fichier est supprimé après analyse."""
    upload_validator = UploadValidator()
    temp_upload_file_manager = TempUploadFileManager(MAX_UPLOAD_SIZE)
    upload_validator.validate_extension(file.filename)

    tmp_path = await temp_upload_file_manager.save(file)

    try:
        audio, sr = librosa.load(tmp_path, sr=SAMPLE_RATE, mono=True)
        features = AudioFeatureExtractor.extract(audio, sr)
        classifier = MusicClassifier(audio_model, sample_rate=SAMPLE_RATE)
        classification = classifier.classify(audio, top_k_per_category=top_k)
    finally:
        temp_upload_file_manager.cleanup(tmp_path)

    return {
        "filename": file.filename,
        **features,
        **classification,
    }


@app.get("/health")
async def health():
    model_info = audio_model.get_model_info() if audio_model else None
    return {"status": "ok", "model_info": model_info}


@app.get("/labels", dependencies=[Depends(_verify_token)])
async def get_default_labels():
    """Retourne la liste des labels par défaut."""
    return {"labels": SOUNDBOARD_LABELS}
