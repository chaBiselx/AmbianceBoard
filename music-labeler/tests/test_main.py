from fastapi.testclient import TestClient
import pytest

import main
from app.classification.labels import SOUNDBOARD_LABELS


class FakeClapAudioModel:
    def get_model_info(self) -> dict:
        return {
            "model_name": "fake/clap-model",
            "text_embed_dim": 128,
            "audio_embed_dim": 64,
        }


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(main, "ClapAudioModel", FakeClapAudioModel)
    monkeypatch.setattr(main, "audio_model", None)
    monkeypatch.setattr(main, "API_TOKEN", "")

    with TestClient(main.app) as test_client:
        yield test_client


def test_routes_reject_invalid_http_methods(client):
    assert client.get("/label").status_code == 405
    assert client.post("/health").status_code == 405
    assert client.post("/labels").status_code == 405


def test_health_returns_status_and_model_info(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "model_info": {
            "model_name": "fake/clap-model",
            "text_embed_dim": 128,
            "audio_embed_dim": 64,
        },
    }


def test_get_labels_requires_token_when_configured(monkeypatch, client):
    monkeypatch.setattr(main, "API_TOKEN", "secret-token")

    response = client.get("/labels")

    assert response.status_code == 401
    assert response.json() == {"detail": "Token invalide ou manquant"}


def test_get_labels_returns_default_labels_with_valid_token(monkeypatch, client):
    monkeypatch.setattr(main, "API_TOKEN", "secret-token")

    response = client.get("/labels", headers={"Authorization": "Bearer secret-token"})

    assert response.status_code == 200
    assert response.json() == {"labels": SOUNDBOARD_LABELS}


def test_label_upload_requires_token_when_configured(monkeypatch, client):
    monkeypatch.setattr(main, "API_TOKEN", "secret-token")

    response = client.post(
        "/label",
        files={"file": ("battle.mp3", b"fake-audio", "audio/mpeg")},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Token invalide ou manquant"}


def test_label_upload_rejects_out_of_range_top_k(client):
    response = client.post(
        "/label?top_k=0",
        files={"file": ("battle.mp3", b"fake-audio", "audio/mpeg")},
    )

    assert response.status_code == 422


def test_label_upload_returns_audio_features_and_labels(monkeypatch, client):
    observed = {}

    def fake_validate_extension(self, filename: str) -> None:
        observed["validated_filename"] = filename

    async def fake_save(self, upload_file) -> str:
        observed["saved_filename"] = upload_file.filename
        return "/tmp/fake-upload.mp3"

    def fake_cleanup(tmp_path: str) -> None:
        observed["cleaned_path"] = tmp_path

    def fake_load(tmp_path: str, sr: int, mono: bool):
        observed["loaded_args"] = (tmp_path, sr, mono)
        return [0.1, -0.2, 0.3], sr

    def fake_extract(audio, sr: int) -> dict:
        observed["feature_args"] = (list(audio), sr)
        return {"bpm": 120.5, "duration_seconds": 3.25}

    class FakeMusicClassifier:
        def __init__(self, model, sample_rate: int) -> None:
            observed["classifier_init"] = (model, sample_rate)

        def classify(self, audio, top_k_per_category: int) -> dict:
            observed["classify_args"] = (list(audio), top_k_per_category)
            return {
                "technical": [
                    {"label": "loop", "score": 0.99},
                ]
            }

    monkeypatch.setattr(main.UploadValidator, "validate_extension", fake_validate_extension)
    monkeypatch.setattr(main.TempUploadFileManager, "save", fake_save)
    monkeypatch.setattr(main.TempUploadFileManager, "cleanup", staticmethod(fake_cleanup))
    monkeypatch.setattr(main.librosa, "load", fake_load)
    monkeypatch.setattr(main.AudioFeatureExtractor, "extract", staticmethod(fake_extract))
    monkeypatch.setattr(main, "MusicClassifier", FakeMusicClassifier)

    response = client.post(
        "/label?top_k=2",
        files={"file": ("battle.mp3", b"fake-audio", "audio/mpeg")},
    )

    assert response.status_code == 200
    assert response.json() == {
        "filename": "battle.mp3",
        "bpm": 120.5,
        "duration_seconds": 3.25,
        "technical": [
            {"label": "loop", "score": 0.99},
        ],
    }
    assert observed == {
        "validated_filename": "battle.mp3",
        "saved_filename": "battle.mp3",
        "loaded_args": ("/tmp/fake-upload.mp3", main.SAMPLE_RATE, True),
        "feature_args": ([0.1, -0.2, 0.3], main.SAMPLE_RATE),
        "classifier_init": (main.audio_model, main.SAMPLE_RATE),
        "classify_args": ([0.1, -0.2, 0.3], 2),
        "cleaned_path": "/tmp/fake-upload.mp3",
    }