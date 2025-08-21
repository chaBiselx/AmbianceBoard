from django.db import models
from main.models.User import User
from main.domain.common.enum.ModerationEnum import ModerationEnum
from main.domain.common.enum.ModerationModelEnum import ModerationModelEnum
from django.utils import timezone




class UserModerationLog(models.Model):
    """
    Journal des avertissements avec message et tag
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name='UserModerationLogUser')
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name='UserModerationLogModerator')
    message = models.TextField(verbose_name='Message de l\'avertissement', null=False, blank=False)
    tag = models.CharField(
        max_length=50,
        choices=[(tag.name, tag.name) for tag in ModerationEnum],
        verbose_name='Tag de modération'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Date de l\'avertissement'
    )
    model = models.CharField(
        max_length=50,
        verbose_name='Model de d\'origine de l\'avertissement',
        choices=[(tag.name, tag.name) for tag in ModerationModelEnum],
        default='unknown'
    )
    report = models.ForeignKey(
        'ReportContent', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='UserModerationLogReport',  # Nom unique pour l'accessor inverse
    )
    
    
    
