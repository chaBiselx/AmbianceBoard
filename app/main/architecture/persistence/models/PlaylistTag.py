import uuid
from django.utils.text import slugify
from django.db import models
from django.core.validators import MinLengthValidator


class PlaylistTag(models.Model):
    """
    Dedicated tag taxonomy for playlists.

    This model is intentionally separate from the soundboard tag model.
    """

    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    label = models.CharField(
        max_length=80,
        unique=True,
        db_index=True,
        help_text="Unique label without spaces used in URLs and filters",
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        validators=[MinLengthValidator(3)],
        help_text="Playlist tag name (3-50 characters)",
    )
    description = models.TextField(
        max_length=200,
        blank=True,
        help_text="Optional playlist tag description",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this playlist tag can be used for filtering",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Playlist Tag"
        verbose_name_plural = "Playlist Tags"

    def __str__(self) -> str:
        return f"{self.name}"

    def clean(self) -> None:
        if self.name:
            self.name = self.name.strip().lower()
        if self.label:
            self.label = slugify(self.label.strip())

        if not self.label and self.name:
            self.label = self._build_unique_label(self.name)

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.strip().lower()
        if self.label:
            self.label = slugify(self.label.strip())
        if not self.label and self.name:
            self.label = self._build_unique_label(self.name)
        super().save(*args, **kwargs)

    def _build_unique_label(self, source: str) -> str:
        base = slugify(source) or "playlist-tag"
        candidate = base
        index = 2

        while PlaylistTag.objects.filter(label=candidate).exclude(pk=self.pk).exists():
            candidate = f"{base}-{index}"
            index += 1

        return candidate
