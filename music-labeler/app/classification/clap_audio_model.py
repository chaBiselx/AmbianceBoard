import os
import numpy as np
import torch
from transformers import ClapModel, ClapProcessor

from app.classification.audio_model import IAudioModel


class ClapAudioModel(IAudioModel):
    """Implementation IAudioModel basee sur le modele CLAP (laion/clap-htsat-unfused)."""
    model_name = os.getenv("CLAP_MODEL", "laion/clap-htsat-unfused")
    

    def __init__(self) -> None:
        print(f"[ClapAudioModel] Loading model {self.model_name} …")
        self._processor = ClapProcessor.from_pretrained(self.model_name)
        self._model = ClapModel.from_pretrained(self.model_name)
        self._model.eval()
        print("[ClapAudioModel] Model loaded ✓")

    @staticmethod
    def _resolve_projection_dim(projection_layer, fallback_dim: int | None) -> int | None:
        """Resolve output dimension across CLAP/Transformers versions."""
        if projection_layer is None:
            return fallback_dim

        direct_dim = getattr(projection_layer, "out_features", None)
        if isinstance(direct_dim, int):
            return direct_dim

        for attr_name in ("projection_dim", "output_dim", "hidden_size"):
            attr_value = getattr(projection_layer, attr_name, None)
            if isinstance(attr_value, int):
                return attr_value

        for linear_name in ("linear", "dense", "projection"):
            linear_layer = getattr(projection_layer, linear_name, None)
            linear_out = getattr(linear_layer, "out_features", None) if linear_layer is not None else None
            if isinstance(linear_out, int):
                return linear_out

        weight = getattr(projection_layer, "weight", None)
        if weight is not None and hasattr(weight, "shape") and len(weight.shape) >= 1:
            return int(weight.shape[0])

        return fallback_dim
        
    def get_model_info(self) -> dict:
        """Retourne des infos sur le modèle pour debug."""
        fallback_dim = getattr(self._model.config, "projection_dim", None)
        return {
            "model_name": self.model_name,
            "text_embed_dim": self._resolve_projection_dim(self._model.text_projection, fallback_dim),
            "audio_embed_dim": self._resolve_projection_dim(self._model.audio_projection, fallback_dim),
        }

    def encode_text(self, texts: list[str]) -> torch.Tensor:
        """Encode une liste de textes en vecteurs normalises."""
        inputs = self._processor(text=texts, return_tensors="pt", padding=True)
        with torch.no_grad():
            features = self._model.get_text_features(**inputs)
        return features / features.norm(dim=-1, keepdim=True)

    def encode_audio(self, audio: np.ndarray, sample_rate: int) -> torch.Tensor:
        """Encode un signal audio en vecteur normalise."""
        inputs = self._processor(audios=[audio], return_tensors="pt", sampling_rate=sample_rate)
        with torch.no_grad():
            features = self._model.get_audio_features(**inputs)
        return features / features.norm(dim=-1, keepdim=True)
