from abc import ABC, abstractmethod

import numpy as np
import torch


class IAudioModel(ABC):
    """Interface pour un modele d'encodage audio/texte zero-shot.

    Pour ajouter un nouveau modele, creer une classe qui herite de IAudioModel
    et implementer encode_text() et encode_audio().
    """

    @abstractmethod
    def encode_text(self, texts: list[str]) -> torch.Tensor:
        """Encode une liste de textes en vecteurs normalises.

        Args:
            texts: liste de descriptions textuelles

        Returns:
            Tensor de shape (len(texts), embed_dim), normalise L2
        """
        ...

    @abstractmethod
    def encode_audio(self, audio: np.ndarray, sample_rate: int) -> torch.Tensor:
        """Encode un signal audio en vecteur normalise.

        Args:
            audio: signal mono float32
            sample_rate: taux d'echantillonnage en Hz

        Returns:
            Tensor de shape (1, embed_dim), normalise L2
        """
        ...
