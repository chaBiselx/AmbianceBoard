import numpy as np
from scipy.signal import stft


class AudioFeatureExtractor:
    """Extraction des metadonnees audio de base."""

    @staticmethod
    def _estimate_tempo(audio: np.ndarray, sr: int) -> float:
        """Estime un tempo musical (BPM) via spectral flux + autocorrelation."""
        if audio.size == 0 or sr <= 0:
            return 0.0

        signal = np.asarray(audio, dtype=np.float32)
        if signal.ndim != 1:
            signal = np.mean(signal, axis=0)

        nperseg = min(2048, max(512, int(sr * 0.046)))
        hop = max(1, nperseg // 4)
        noverlap = nperseg - hop
        _, _, spectrum = stft(
            signal,
            fs=sr,
            window="hann",
            nperseg=nperseg,
            noverlap=noverlap,
            boundary=None,
            padded=False,
        )
        magnitude = np.abs(spectrum)
        if magnitude.shape[1] < 3:
            return 0.0

        # Onset envelope robuste: flux spectral positif (accentue les attaques musicales).
        spectral_flux = np.diff(magnitude, axis=1)
        spectral_flux = np.maximum(spectral_flux, 0.0).sum(axis=0)
        if not np.any(spectral_flux):
            return 0.0

        spectral_flux = spectral_flux - np.mean(spectral_flux)
        flux_std = float(np.std(spectral_flux))
        if flux_std <= 1e-8:
            return 0.0
        spectral_flux = spectral_flux / flux_std

        # Tempo plausible pour la musique moderne (60-200 BPM).
        hop_seconds = hop / float(sr)
        min_bpm = 60.0
        max_bpm = 240.0
        lag_min = int(round((60.0 / max_bpm) / hop_seconds))
        lag_max = int(round((60.0 / min_bpm) / hop_seconds))
        if lag_max <= lag_min:
            return 0.0

        autocorr = np.correlate(spectral_flux, spectral_flux, mode="full")
        autocorr = autocorr[len(spectral_flux) - 1:]
        if lag_max >= autocorr.size:
            lag_max = autocorr.size - 1
        if lag_min < 1 or lag_min >= lag_max:
            return 0.0

        lags = np.arange(lag_min, lag_max + 1)
        scores = autocorr[lags].copy()

        # Renforce les rapports metriques usuels (double/half-time).
        double_lags = lags * 2
        valid_double = double_lags < autocorr.size
        scores[valid_double] += 0.45 * autocorr[double_lags[valid_double]]

        half_lags = np.maximum(1, lags // 2)
        valid_half = half_lags >= lag_min
        scores[valid_half] += 0.25 * autocorr[half_lags[valid_half]]

        # Petit prior musical pour stabiliser vers une zone de tempo naturelle.
        bpm_candidates = 60.0 / (lags * hop_seconds)
        prior = np.exp(-0.5 * ((bpm_candidates - 120.0) / 40.0) ** 2)
        scores *= prior

        best_idx = int(np.argmax(scores))
        best_lag = int(lags[best_idx])
        if best_lag <= 0:
            return 0.0

        bpm = 60.0 / (best_lag * hop_seconds)
        return float(np.clip(bpm, 30.0, 240.0))

    @staticmethod
    def extract(audio: np.ndarray, sr: int) -> dict:
        """Extract basic audio features."""
        bpm = AudioFeatureExtractor._estimate_tempo(audio, sr)
        return {
            "bpm": round(bpm, 1),
            "duration_seconds": round(float(len(audio) / sr), 2),
        }
