from types import SimpleNamespace
from unittest.mock import MagicMock

import numpy as np
import torch

from app.classification.clap_audio_model import ClapAudioModel


def _build_model_with_mocks(monkeypatch):
    processor_instance = MagicMock(name="processor")
    model_instance = MagicMock(name="model")
    model_instance.config = SimpleNamespace(projection_dim=256)

    processor_cls = MagicMock(name="ClapProcessor")
    processor_cls.from_pretrained.return_value = processor_instance

    model_cls = MagicMock(name="ClapModel")
    model_cls.from_pretrained.return_value = model_instance

    monkeypatch.setattr("app.classification.clap_audio_model.ClapProcessor", processor_cls)
    monkeypatch.setattr("app.classification.clap_audio_model.ClapModel", model_cls)
    monkeypatch.setattr(ClapAudioModel, "model_name", "mock/clap-model")

    sut = ClapAudioModel()
    return sut, processor_instance, model_instance, processor_cls, model_cls


def test_init_loads_processor_and_model(monkeypatch):
    sut, _, model_instance, processor_cls, model_cls = _build_model_with_mocks(monkeypatch)

    processor_cls.from_pretrained.assert_called_once_with("mock/clap-model")
    model_cls.from_pretrained.assert_called_once_with("mock/clap-model")
    model_instance.eval.assert_called_once_with()
    assert sut.model_name == "mock/clap-model"


def test_resolve_projection_dim_supports_multiple_shapes():
    assert ClapAudioModel._resolve_projection_dim(None, 42) == 42

    direct = SimpleNamespace(out_features=512)
    assert ClapAudioModel._resolve_projection_dim(direct, 1) == 512

    from_projection_attr = SimpleNamespace(projection_dim=384)
    assert ClapAudioModel._resolve_projection_dim(from_projection_attr, 1) == 384

    nested_linear = SimpleNamespace(linear=SimpleNamespace(out_features=768))
    assert ClapAudioModel._resolve_projection_dim(nested_linear, 1) == 768

    weight_fallback = SimpleNamespace(weight=torch.zeros(300, 10))
    assert ClapAudioModel._resolve_projection_dim(weight_fallback, 1) == 300

    unknown = SimpleNamespace()
    assert ClapAudioModel._resolve_projection_dim(unknown, 99) == 99


def test_get_model_info_uses_projection_resolver(monkeypatch):
    sut, _, model_instance, _, _ = _build_model_with_mocks(monkeypatch)
    model_instance.text_projection = SimpleNamespace(out_features=128)
    model_instance.audio_projection = SimpleNamespace(linear=SimpleNamespace(out_features=64))

    info = sut.get_model_info()

    assert info == {
        "model_name": "mock/clap-model",
        "text_embed_dim": 128,
        "audio_embed_dim": 64,
    }


def test_encode_text_normalizes_features(monkeypatch):
    sut, processor_instance, model_instance, _, _ = _build_model_with_mocks(monkeypatch)
    processor_instance.return_value = {"input_ids": torch.tensor([[1, 2]])}
    model_instance.get_text_features.return_value = torch.tensor([[3.0, 4.0]])

    result = sut.encode_text(["rain", "forest"])

    processor_instance.assert_called_once_with(text=["rain", "forest"], return_tensors="pt", padding=True)
    model_instance.get_text_features.assert_called_once()
    _, kwargs = model_instance.get_text_features.call_args
    assert torch.equal(kwargs["input_ids"], torch.tensor([[1, 2]]))
    assert torch.allclose(result, torch.tensor([[0.6, 0.8]]), atol=1e-6)
    assert torch.allclose(result.norm(dim=-1), torch.ones(1), atol=1e-6)


def test_encode_audio_normalizes_features(monkeypatch):
    sut, processor_instance, model_instance, _, _ = _build_model_with_mocks(monkeypatch)
    audio = np.array([0.1, -0.2, 0.3], dtype=np.float32)
    processor_instance.return_value = {"input_features": torch.tensor([[1.0, 2.0]])}
    model_instance.get_audio_features.return_value = torch.tensor([[0.0, 5.0]])

    result = sut.encode_audio(audio, sample_rate=16_000)

    assert processor_instance.call_count == 1
    _, kwargs = processor_instance.call_args
    assert kwargs["return_tensors"] == "pt"
    assert kwargs["sampling_rate"] == 16_000
    assert len(kwargs["audio"]) == 1
    np.testing.assert_allclose(kwargs["audio"][0], audio)

    model_instance.get_audio_features.assert_called_once()
    _, kwargs = model_instance.get_audio_features.call_args
    assert torch.equal(kwargs["input_features"], torch.tensor([[1.0, 2.0]]))
    assert torch.allclose(result, torch.tensor([[0.0, 1.0]]), atol=1e-6)
    assert torch.allclose(result.norm(dim=-1), torch.ones(1), atol=1e-6)
