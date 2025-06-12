import uuid
from django.db import models
from home.models.Playlist import Playlist
from home.enum.ReportContentResultEnum import ReportContentResultEnum

class ReportContent(models.Model):
    id = models.BigAutoField(primary_key=True) 
    creator = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='created_reports'  # Nom unique pour l'accessor inverse
    )
    typeElement = models.CharField(
        max_length=25,
        choices=[('playlist', 'playlist'), ('soundboard', 'soundboard')],
        verbose_name='Type de contenu'
    )
    uuidElement = models.UUIDField(db_index=True)
    precisionElement = models.CharField(
        max_length=25,
        choices=[('unknown', 'unknown'), ('image', 'image'), ('text', 'text'), ('music', 'music'), ('copyright', 'copyright')],
        verbose_name='precision sur l\'élément'
    )
    descriptionElement = models.TextField(verbose_name='Description de l\'élément')
    created_at = models.DateTimeField(auto_now_add=True)
    
    moderator = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='moderated_reports',  # Nom unique pour l'accessor inverse
        verbose_name='moderateur'
    )
    resultModerator = models.CharField(
        max_length=25,
        choices=([tag.name, tag.name] for tag in ReportContentResultEnum),
        verbose_name='Resultat moderateur'
    )
    dateResultModerator = models.DateTimeField(null=True, blank=True, verbose_name='Date de la modération')
    
    def __str__(self):
        return f'{self.typeElement}  {self.precisionElement} {self.uuidElement}'