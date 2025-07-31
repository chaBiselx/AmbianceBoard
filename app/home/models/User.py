from typing import Optional
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils import timezone
from encrypted_model_fields.fields import EncryptedCharField


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True) 
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    first_name = EncryptedCharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="Prénom de l'utilisateur"
    )
    last_name = EncryptedCharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="Nom de famille de l'utilisateur"
    )
    username = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='username',
        help_text="Nom d'utilisateur",
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    isBan = models.BooleanField(default=False, help_text="Indicates if the user is banned")
    isConfirmed = models.BooleanField(default=False, help_text="Indicates if the user's email is confirmed")
    confirmationToken = models.CharField(max_length=255, default=None, null=True, blank=True)
    demandeConfirmationDate = models.DateTimeField(default=None, null=True, blank=True)
    reasonBan = models.CharField(max_length=255, default="" , null=False, blank=True)
    banExpiration = models.DateTimeField(default=None, null=True, blank=True) 
    tokenReinitialisation = models.CharField(max_length=255, default=None, null=True, blank=True)
    demandeTokenDate = models.DateTimeField(default=None, null=True, blank=True)
    betaTester = models.BooleanField(default=False, help_text="Indicates if the user is a beta tester")
    
    
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
    
    def __str__(self) -> str:
        return f"{self.username} {self.email}"
    
    def get_confirmation_token(self) -> Optional[str]:
        return str(self.confirmationToken) if self.confirmationToken is not None else self.confirmationToken
    
    def get_reinitialisation_token(self) -> Optional[str]:
        return str(self.tokenReinitialisation) if self.tokenReinitialisation is not None else self.tokenReinitialisation
        
        
        