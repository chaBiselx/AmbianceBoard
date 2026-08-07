import uuid
from urllib.parse import urlparse
from django.db import models
from django.utils import timezone
from main.architecture.persistence.models.User import User


class TrafficAttributionVisit(models.Model):
    """Stocke les visites publiques avec attribution referer/UTM."""

    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Utilisateur associe a la visite si connecte"
    )
    is_authenticated = models.BooleanField(default=False)

    visited_at = models.DateTimeField(default=timezone.now, db_index=True)
    path = models.CharField(max_length=1024, blank=True, default="")
    uri = models.URLField(max_length=2000, blank=True, default="")

    referer_url = models.URLField(max_length=2000, blank=True, default="")
    referer_domain = models.CharField(max_length=255, blank=True, default="direct", db_index=True)

    session_key = models.CharField(max_length=40, blank=True, default="", db_index=True)

    utm_data = models.JSONField(default=dict, blank=True)
    utm_source = models.CharField(max_length=255, blank=True, default="", db_index=True)

    class Meta:
        verbose_name = "Visite avec attribution"
        verbose_name_plural = "Visites avec attribution"
        ordering = ['-visited_at']
        indexes = [
            models.Index(fields=['visited_at']),
            models.Index(fields=['referer_domain', 'visited_at']),
            models.Index(fields=['utm_source', 'visited_at']),
        ]

    def __str__(self) -> str:
        source = self.utm_source or self.referer_domain or "unknown"
        return f"{source} - {self.visited_at}"

    @staticmethod
    def extract_referer_domain(referer_url: str, host: str = "") -> str:
        """Retourne un domaine normalize pour les graphes d'attribution."""
        if not referer_url:
            return "direct"

        parsed = urlparse(referer_url)
        referer_host = (parsed.hostname or "").lower()
        current_host = (host or "").split(':')[0].lower()

        if not referer_host:
            return "direct"

        if current_host and referer_host == current_host:
            return "internal"

        return referer_host
