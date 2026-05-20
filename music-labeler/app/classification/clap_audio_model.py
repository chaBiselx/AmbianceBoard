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
        
    def get_model_info(self) -> dict:
        """Retourne des infos sur le modèle pour debug."""
        return {
            "model_name": self.model_name,
            "text_embed_dim": self._model.text_projection.out_features,
            "audio_embed_dim": self._model.audio_projection.out_features,
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
