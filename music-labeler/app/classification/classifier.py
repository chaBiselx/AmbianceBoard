import numpy as np
import torch

from app.classification.audio_model import IAudioModel
from app.classification.labels import CATEGORY_DESCRIPTIONS, MACRO_TYPES, SOUNDBOARD_LABELS


class MusicClassifier:
    """Encapsule la logique de classification en 3 passes (independant du modele)."""

    second_best_type_diff = 0.25
    temperature = 0.065  # Plus bas = scores plus tranches, plus haut = distribution plus lisse

    def __init__(self, model: IAudioModel, sample_rate: int) -> None:
        self.model = model
        self.sample_rate = sample_rate

    def classify(self, audio: np.ndarray, top_k_per_category: int = 3) -> dict:
        """Classification en 3 passes : macro-type -> categorie -> labels."""
        audio_features = self.model.encode_audio(audio, self.sample_rate)

        best_macro, macro_names, macro_probs, relevant_categories = self._classify_macro_type(audio_features)
        cat_names, cat_probs = self._score_categories(audio_features)
        results = self._classify_labels(
            audio_features,
            cat_names,
            cat_probs,
            relevant_categories,
            top_k_per_category,
        )

        return {
            "macro_type": best_macro,
            "macro_confidences": {
                macro_names[i]: round(float(macro_probs[i]), 4) for i in range(len(macro_names))
            },
            "categories": results,
        }

    def classify_zero_shot(self, audio: np.ndarray, labels: list[str], top_k: int, display_names: list[str] | None = None) -> list[dict]:
        """Run CLAP zero-shot classification and return top-k labels."""
        text_features = self.model.encode_text(labels)
        audio_features = self.model.encode_audio(audio, self.sample_rate)
        similarity = (audio_features @ text_features.T).squeeze(0)

        probs = (similarity / self.temperature).softmax(dim=-1).numpy()

        top_indices = np.argsort(probs)[::-1][:top_k]
        names = display_names if display_names and len(display_names) == len(labels) else labels
        return [
            {"label": names[i], "confidence": round(float(probs[i]), 4)}
            for i in top_indices
        ]

    def _classify_macro_type(self, audio_features: torch.Tensor) -> tuple[str, list[str], np.ndarray, set[str]]:
        """Classifie le macro-type principal et determine les categories pertinentes."""
        macro_names = list(MACRO_TYPES.keys())
        macro_texts = [MACRO_TYPES[m]["description"] for m in macro_names]
        macro_features = self.model.encode_text(macro_texts)

        macro_similarity = (audio_features @ macro_features.T).squeeze(0)
        macro_probs = (macro_similarity / self.temperature).softmax(dim=-1).numpy()

        best_macro_idx = int(np.argmax(macro_probs))
        best_macro = macro_names[best_macro_idx]
        relevant_categories = set(MACRO_TYPES[best_macro]["categories"])

        sorted_macro_idx = np.argsort(macro_probs)[::-1]
        second_macro_idx = int(sorted_macro_idx[1])
        if macro_probs[best_macro_idx] - macro_probs[second_macro_idx] < self.second_best_type_diff:
            second_macro = macro_names[second_macro_idx]
            relevant_categories |= set(MACRO_TYPES[second_macro]["categories"])

        return best_macro, macro_names, macro_probs, relevant_categories

    def _score_categories(self, audio_features: torch.Tensor) -> tuple[list[str], np.ndarray]:
        """Calcule les scores de similarite pour toutes les categories."""
        cat_names = list(CATEGORY_DESCRIPTIONS.keys())
        cat_texts = list(CATEGORY_DESCRIPTIONS.values())
        cat_features = self.model.encode_text(cat_texts)

        cat_similarity = (audio_features @ cat_features.T).squeeze(0)
        cat_probs = (cat_similarity / self.temperature).softmax(dim=-1).numpy()
        return cat_names, cat_probs

    def _classify_labels(
        self,
        audio_features: torch.Tensor,
        cat_names: list[str],
        cat_probs: np.ndarray,
        relevant_categories: set[str],
        top_k_per_category: int,
    ) -> dict:
        """Classifie les labels uniquement pour les categories pertinentes."""
        results = {}
        for i, cat_name in enumerate(cat_names):
            if cat_name not in relevant_categories:
                continue

            cat_labels = SOUNDBOARD_LABELS[cat_name]
            enriched = [f"{label.replace('-', ' ')} sound" for label in cat_labels]
            label_features = self.model.encode_text(enriched)

            label_similarity = (audio_features @ label_features.T).squeeze(0)
            label_probs = (label_similarity / self.temperature).softmax(dim=-1).numpy()

            top_idx = np.argsort(label_probs)[::-1][:top_k_per_category]
            results[cat_name] = {
                "category_confidence": round(float(cat_probs[i]), 4),
                "labels": [
                    {"label": cat_labels[j], "confidence": round(float(label_probs[j]), 4)}
                    for j in top_idx
                ],
            }

        return results
