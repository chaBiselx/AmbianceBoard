from django.db import models
from django.core.exceptions import ValidationError


class SoundboardSection(models.Model):
    SoundBoard = models.ForeignKey(
        "SoundBoard",
        on_delete=models.CASCADE,
        related_name="sections",
        null=False,
        blank=False,
    )
    name = models.CharField(max_length=255, default="", blank=True)
    section = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["section", "order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["SoundBoard", "section"],
                name="unique_soundboard_section_number",
            )
        ]

    def clean(self):
        super().clean()
        if self.section < 1:
            raise ValidationError("La section doit être supérieure ou égale à 1.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        name = self.name or f"Section {self.section}"
        
        return self.SoundBoard.name + " - " + name

    def get_name(self):
        return self.name or f"Section {self.section}"
