from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils import timezone

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    isBan = models.BooleanField(default=False)
    isConfirmed = models.BooleanField(default=False)
    confirmationToken = models.CharField(max_length=255, default=None, null=True, blank=True)
    demandeConfirmationDate = models.DateTimeField(default=None, null=True, blank=True)
    reasonBan = models.CharField(max_length=255, default="")
    banExpiration = models.DateTimeField(default=None, null=True, blank=True) 
    
    def checkBanned(self) -> bool:
        """
        Check if the user is banned.

        Returns:
            bool: True if the user is banned and the ban is still active, 
                False if the user is not banned or the ban has expired.
        """
        if(self.isBan == False):
            return False
        if self.banExpiration is not None:
            return self.banExpiration >= timezone.now()
        return True
    
    def __str__(self):
        return f"{self.username} {self.email}"
    
    def get_confirmation_token(self) -> str|None:
        return str(self.confirmationToken) if self.confirmationToken is not None else self.confirmationToken
    
        
        