from django.db import models
from django.core.exceptions import ValidationError


class SoundboardPlaylist(models.Model):
    Playlist = models.ForeignKey("Playlist", on_delete=models.CASCADE, null=False, blank=False)
    section = models.ForeignKey(
        "SoundboardSection",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="playlists",
    )
    order = models.IntegerField(default=0)
    activable_by_player = models.BooleanField(default=False)
    shortcut_keyboard = models.JSONField(null=True, blank=True)

    def clean(self):
        super().clean()
        if self.section is not None and self.section.section < 1:
            raise ValidationError("La section doit être supérieure ou égale à 1.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        section_label = self.section.get_name() if self.section else "Sans section"
        return f"{self.section.SoundBoard} - {self.Playlist} - {section_label} - Ordre {self.order}"

    def meta(self):
        return {
            "SoundBoard": self.section.SoundBoard if self.section else None,
            "Playlist": self.Playlist,
            "order": self.order,
            "section": self.section,
        }

    def get_section(self):
        if self.section is None:
            return 1
        if isinstance(self.section, int):
            return self.section
        return self.section.section

    def get_playlist(self):
        return self.Playlist
