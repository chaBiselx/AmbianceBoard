import os
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

import librosa
import numpy as np
import torch
from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from transformers import ClapModel, ClapProcessor

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL_NAME = os.getenv("CLAP_MODEL", "laion/clap-htsat-unfused")
API_TOKEN = os.getenv("MUSIC_LABELER_TOKEN", "")
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".webm"}
MAX_UPLOAD_SIZE = 35 * 1024 * 1024  # 35 Mo
SAMPLE_RATE = 48_000

# Labels par défaut orientés JDR / soundboard
# CLAP fonctionne mieux avec des descriptions phrasées et des catégories distinctes

SOUNDBOARD_LABELS = {
    "environment": [
        "forest", "night-forest", "jungle", "swamp", "plains",
        "desert", "tundra", "mountain", "cave", "coast",
        "city", "village", "tavern", "castle", "dungeon",
        "temple", "ruins", "sewers", "harbor", "market",
        "interior", "exterior", "underground", "underwater", "aerial",
        "space", "astral-plane", "hell", "paradise", "void",
    ],
    "weather": [
        "light-rain", "heavy-rain", "storm", "thunder", "wind",
        "tempest", "blizzard", "fog", "calm-night", "dawn",
        "twilight", "heat", "cold", "silence", "day-ambience",
        "night-ambience",
    ],
    "music_style": [
        "orchestral", "epic-orchestral", "dramatic-orchestral", "soft-orchestral",
        "medieval", "celtic", "folk", "bard",
        "rock", "metal", "symphonic-metal",
        "electronic", "ambient", "dark-ambient", "synthwave",
        "jazz", "blues", "gospel",
        "tribal", "shamanic", "oriental", "asian",
        "classical", "baroque", "choir", "acapella",
        "lo-fi", "minimalist", "drone", "generic",
        "tension-build", "stinger", "sting", "jingle",
    ],
    "rolestyle": [
        "horror", "cosmic-horror", "supernatural-horror", "psychological-horror",
        "comedy", "parody", "burlesque",
        "epic", "heroic", "legendary",
        "romantic", "melancholic", "nostalgic",
        "mystery", "suspense", "thriller",
        "tragic", "dramatic", "emotional",
        "dark", "grimdark", "oppressive",
        "wonderous", "fairy-like", "dreamlike",
        "neutral", "slice-of-life", "everyday-life",
    ],
    "action": [
        "combat", "epic-combat", "loss-combat", "boss-fight", "ambush", "escape",
        "investigation", "exploration", "infiltration", "negotiation", "diplomacy",
        "journey", "crossing", "rest", "camp",
        "ritual", "magic", "summoning", "curse",
        "chase", "race", "hunt",
        "revelation", "twist", "climax", "resolution",
        "pc-death", "victory", "defeat", "betrayal",
        "puzzle", "trap", "riddle",
        "celebration", "ceremony", "festival",
    ],
    "creature": [
        "humanoid", "monster", "dragon", "undead", "demon",
        "angel", "fairy", "beast", "mechanical", "eldritch",
        "insectoid", "aquatic", "flying", "invisible", "spirit",
        "robot", "alien", "mythical", "giant", "swarm",
        "animal", "bird", "fish", "reptile", "amphibian",
    ],
    "genre": [
        "fantasy", "high-fantasy", "low-fantasy", "dark-fantasy",
        "science-fiction", "space-opera", "cyberpunk", "steampunk", "dieselpunk",
        "contemporary", "historical", "antiquity", "medieval-fantasy",
        "post-apocalyptic", "western", "piracy",
        "lovecraftian", "gothic", "victorian",
        "superhero", "urban-fantasy", "modern-horror",
        "oneshot", "campaign", "sandbox",
    ],
    "technical": [
        "loop", "one-shot", "intro", "outro", "transition",
        "background-sound", "foreground", "sfx", "music", "voice-over",
        "low-intensity", "medium-intensity", "high-intensity",
        "slow-tempo", "medium-tempo", "fast-tempo",
        "major-key", "minor-key",
        "instrumental", "with-lyrics",
        "short-duration", "long-duration",
    ],
    "sfx": [
        # Explosions / destruction
        "explosion",  "shockwave",
        "blast", "detonation", "collapse", "destruction", "debris",

        # Impacts / hits
        "impact", "heavy-impact", "light-impact", "hit", "slam",
        "crash", "thud", "smash", "punch", "kick",
        "gunshot", "ricochet", "bullet-impact", "arrow-hit",
        "sword-clash", "metal-impact", "bone-crack",

        # Interference / glitches
        "interference", "radio-interference", "signal-loss", "static",
        "glitch", "distortion", "feedback", "scramble",
        "transmission", "corrupted-audio",

        # Energy / sci-fi
        "laser", "plasma-shot", "energy-burst", "electric-zap",
        "electromagnetic-pulse", "force-field", "shield-hit",
        "teleport", "warp", "scanner",

        # Horror / tension
        "scream", "whisper", "heartbeat", "breathing",
        "creak", "scratch", "growl", "monster-roar",
        "jump-scare", "tension-hit",

        # Environment interactions
        "door-open", "door-close", "door-creak",
        "footsteps", "running", "glass-break",
        "chain-rattle", "fire-crackle", "water-splash",
        "machine", "engine", "alarm", "siren",

        # UI / system sounds
        "notification", "button-click", "beep", "warning",
        "success", "failure", "countdown", "system-error",

        # Transitional / cinematic
        "whoosh", "rise", "drop", "transition-hit",
        "cinematic-boom", "reverse-hit", "stinger-sfx",
    ]
}



# ---------------------------------------------------------------------------
# Model holder (loaded once at startup)
# ---------------------------------------------------------------------------
model: ClapModel | None = None
processor: ClapProcessor | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global model, processor
    print(f"[music-labeler] Loading model {MODEL_NAME} …")
    processor = ClapProcessor.from_pretrained(MODEL_NAME)
    model = ClapModel.from_pretrained(MODEL_NAME)
    model.eval()
    print("[music-labeler] Model loaded ✓")
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
# Helpers
# ---------------------------------------------------------------------------

def _classify(audio: np.ndarray, labels: list[str], top_k: int, display_names: list[str] | None = None) -> list[dict]:
    """Run CLAP zero-shot classification and return top-k labels."""
    text_inputs = processor(text=labels, return_tensors="pt", padding=True)
    audio_inputs = processor(
        audios=[audio],
        return_tensors="pt",
        sampling_rate=SAMPLE_RATE,
    )

    with torch.no_grad():
        text_features = model.get_text_features(**text_inputs)
        audio_features = model.get_audio_features(**audio_inputs)

    text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    audio_features = audio_features / audio_features.norm(dim=-1, keepdim=True)
    similarity = (audio_features @ text_features.T).squeeze(0)

    # Température pour rendre la distribution plus tranchée
    temperature = 0.07
    probs = (similarity / temperature).softmax(dim=-1).numpy()

    top_indices = np.argsort(probs)[::-1][:top_k]
    names = display_names if display_names and len(display_names) == len(labels) else labels
    return [
        {"label": names[i], "confidence": round(float(probs[i]), 4)}
        for i in top_indices
    ]


def _classify_by_category(audio: np.ndarray, top_k_per_category: int = 3) -> dict:
    """Classification en 3 passes : macro-type → catégorie → labels."""

    # Macro-types : regroupe les catégories par nature sonore
    MACRO_TYPES = {
        "INSTANT": {
            "description": "short instantaneous sound effect or creature vocalization like explosion hit roar screech gunshot",
            "categories": ["sfx", "creature", "action"],
        },
        "AMBIANCE": {
            "description": "continuous diegetic ambient background sound like ocean waves fire crackling rain forest wind city noise",
            "categories": ["environment", "weather", "creature"],
        },
        "MUSIC": {
            "description": "extradiegetic music soundtrack or musical score like orchestral combat chase theme dramatic melody",
            "categories": ["music_style", "rolestyle", "action", "genre", "technical"],
        },
    }

    # Descriptions phrasées pour chaque catégorie (CLAP comprend mieux les phrases)
    category_descriptions = {
        "environment": "ambient background sound of a place or location like forest cave city tavern dungeon",
        "weather": "weather and natural atmosphere sounds like rain thunder wind storm blizzard",
        "music_style": "musical genre and style like orchestral medieval electronic rock jazz folk",
        "rolestyle": "emotional mood and tone like horror epic mysterious dramatic melancholic dark",
        "action": "tabletop RPG scene and action like combat exploration chase ritual celebration",
        "creature": "creature or monster sounds like dragon demon beast undead mechanical",
        "genre": "fictional universe setting like fantasy science fiction steampunk post-apocalyptic",
        "technical": "audio production type like loop intro transition background foreground intensity",
        "sfx": "short sound effect like explosion impact gunshot whoosh glitch interference alarm",
    }

    audio_inputs = processor(
        audios=[audio],
        return_tensors="pt",
        sampling_rate=SAMPLE_RATE,
    )
    with torch.no_grad():
        audio_features = model.get_audio_features(**audio_inputs)
    audio_features = audio_features / audio_features.norm(dim=-1, keepdim=True)

    # Passe 0 : classification macro-type (instantané / ambiance / musique)
    macro_names = list(MACRO_TYPES.keys())
    macro_texts = [MACRO_TYPES[m]["description"] for m in macro_names]
    macro_inputs = processor(text=macro_texts, return_tensors="pt", padding=True)
    with torch.no_grad():
        macro_features = model.get_text_features(**macro_inputs)
    macro_features = macro_features / macro_features.norm(dim=-1, keepdim=True)
    macro_similarity = (audio_features @ macro_features.T).squeeze(0)
    macro_probs = (macro_similarity / 0.07).softmax(dim=-1).numpy()

    best_macro_idx = int(np.argmax(macro_probs))
    best_macro = macro_names[best_macro_idx]
    relevant_categories = set(MACRO_TYPES[best_macro]["categories"])

    # Si le 2e macro-type est proche (écart < 0.25), inclure ses catégories aussi
    sorted_macro_idx = np.argsort(macro_probs)[::-1]
    second_macro_idx = int(sorted_macro_idx[1])
    if macro_probs[best_macro_idx] - macro_probs[second_macro_idx] < 0.25:
        second_macro = macro_names[second_macro_idx]
        relevant_categories |= set(MACRO_TYPES[second_macro]["categories"])

    # Passe 1 : score par catégorie (toutes, pour info)
    cat_names = list(category_descriptions.keys())
    cat_texts = list(category_descriptions.values())
    cat_inputs = processor(text=cat_texts, return_tensors="pt", padding=True)
    with torch.no_grad():
        cat_features = model.get_text_features(**cat_inputs)
    cat_features = cat_features / cat_features.norm(dim=-1, keepdim=True)
    cat_similarity = (audio_features @ cat_features.T).squeeze(0)
    cat_probs = (cat_similarity / 0.07).softmax(dim=-1).numpy()

    # Passe 2 : top labels uniquement dans les catégories pertinentes
    results = {}
    for i, cat_name in enumerate(cat_names):
        if cat_name not in relevant_categories:
            continue

        cat_labels = SOUNDBOARD_LABELS[cat_name]
        # Enrichir les labels avec un contexte pour CLAP
        enriched = [f"{label.replace('-', ' ')} sound" for label in cat_labels]
        label_inputs = processor(text=enriched, return_tensors="pt", padding=True)
        with torch.no_grad():
            label_features = model.get_text_features(**label_inputs)
        label_features = label_features / label_features.norm(dim=-1, keepdim=True)
        label_similarity = (audio_features @ label_features.T).squeeze(0)
        label_probs = (label_similarity / 0.07).softmax(dim=-1).numpy()

        top_idx = np.argsort(label_probs)[::-1][:top_k_per_category]
        results[cat_name] = {
            "category_confidence": round(float(cat_probs[i]), 4),
            "labels": [
                {"label": cat_labels[j], "confidence": round(float(label_probs[j]), 4)}
                for j in top_idx
            ],
        }

    return {
        "macro_type": best_macro,
        "macro_confidences": {
            macro_names[i]: round(float(macro_probs[i]), 4) for i in range(len(macro_names))
        },
        "categories": results,
    }


def _extract_features(audio: np.ndarray, sr: int) -> dict:
    """Extract basic audio features with librosa."""
    tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
    bpm = float(tempo) if isinstance(tempo, (int, float, np.floating)) else float(tempo[0])
    return {
        "bpm": round(bpm, 1),
        "duration_seconds": round(float(len(audio) / sr), 2),
    }


def _validate_extension(filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Format non supporté ({ext}). Formats acceptés : {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/label", dependencies=[Depends(_verify_token)])
async def label_upload(
    file: UploadFile = File(...),
    top_k: int = Query(default=3, ge=1, le=10),
):
    """Labelise un fichier audio uploadé. Le fichier est supprimé après analyse."""
    _validate_extension(file.filename)

    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        size = 0
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD_SIZE:
                tmp.close()
                os.unlink(tmp.name)
                raise HTTPException(
                    status_code=413,
                    detail=f"Fichier trop volumineux. Taille max : {MAX_UPLOAD_SIZE // (1024 * 1024)} Mo",
                )
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        audio, sr = librosa.load(tmp_path, sr=SAMPLE_RATE, mono=True)
        features = _extract_features(audio, sr)
        classification = _classify_by_category(audio, top_k_per_category=top_k)
    finally:
        os.unlink(tmp_path)

    return {
        "filename": file.filename,
        **features,
        **classification,
    }


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_NAME, "model_loaded": model is not None}


@app.get("/labels", dependencies=[Depends(_verify_token)])
async def get_default_labels():
    """Retourne la liste des labels par défaut."""
    return {"labels": SOUNDBOARD_LABELS}
