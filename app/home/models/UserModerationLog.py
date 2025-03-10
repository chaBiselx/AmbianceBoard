from django.db import models
from home.models.User import User
from home.enum.ModerationEnum import ModerationEnum
from django.utils import timezone




class UserModerationLog(models.Model):
    """
    Journal des avertissements avec message et tag
    """
    userOld = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False,to_field='uuid', related_name='UserModerationLogUserOld')
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,to_field='id', related_name='UserModerationLogUser')
    
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
    
    
