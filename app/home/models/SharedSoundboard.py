from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils import timezone
from datetime import datetime, timedelta

class SharedSoundboard(models.Model):
    id = models.BigAutoField(primary_key=True) 
    soundboard = models.ForeignKey('SoundBoard', on_delete=models.CASCADE, null=False, blank=False, related_name='shared')
    token = models.UUIDField(default=uuid.uuid4, editable=False, null=False, blank=False)
    expiration_date = models.DateTimeField(default=timezone.now, null=False, blank=False)
    
    def save(self, *args, **kwargs):
        self.expiration_date = timezone.make_aware(datetime.now() + timedelta(days=10))
        super().save(*args, **kwargs)
    
    
        
        
        