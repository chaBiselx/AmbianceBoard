from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .Track import Track


class TrackLabel(models.Model):
    """
    Stocke les labels IA associés à une Track avec leur score de confiance.
    Permet de taguer les playlists en fonction des tags agrégés de leurs tracks.
    """

    id = models.BigAutoField(primary_key=True)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="labels")
    category = models.CharField(max_length=50, db_index=True)
    label = models.CharField(max_length=100, db_index=True)
    confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-confidence']
        unique_together = [('track', 'category', 'label')]
        verbose_name = "Track Label"
        verbose_name_plural = "Track Labels"
        indexes = [
            models.Index(fields=['track', '-confidence'], name='idx_tracklabel_track_conf'),
            models.Index(fields=['category', 'label'], name='idx_tracklabel_cat_label'),
        ]

    def __str__(self) -> str:
        return f"{self.track_id} — {self.category}/{self.label} ({self.confidence:.0%})"
