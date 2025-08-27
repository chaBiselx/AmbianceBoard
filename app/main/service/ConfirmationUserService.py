from main.utils.logger import LoggerFactory
import uuid
from django.urls import reverse
from main.architecture.persistence.models.User import User
from main.domain.common.exceptions.SecurityException import SecurityException
from django.utils import timezone


class ConfirmationUserService:
    
    def __init__(self, user: User) -> None:
        self.user = user
        self.logger = LoggerFactory.get_default_logger()
    
    def generation_uri(self, change_confirmation_date: bool = True) -> str:
        if self.user.isConfirmed:
            raise SecurityException("User already confirmed")
        self.user.confirmationToken = self.__generation_token()
        if(change_confirmation_date):
            self.user.demandeConfirmationDate = timezone.now()
        self.logger.debug(f"Confirmation token: {self.user.confirmationToken} for user {self.user.username}: ")
        
        self.user.save()
        return reverse("confirm_account", kwargs={'uuid_user': self.user.uuid, 'confirmation_token': self.user.confirmationToken })
    
    def verification_token(self, confirmation_token: str) -> bool:
        if self.user is None : 
            raise SecurityException("User not found")
        if self.user.confirmationToken is None :
            raise SecurityException("Confirmation token not found")
        if confirmation_token is None :
            raise SecurityException("token invalid")
        if self.user.get_confirmation_token() != str(confirmation_token):
            raise SecurityException("Confirmation token dont match")
        if self.user.demandeConfirmationDate is None:
            raise SecurityException("Confirmation date not found")
        if self.user.demandeConfirmationDate + timezone.timedelta(days=1) < timezone.now():
            raise SecurityException("Confirmation date expired")
                
        self.user.isConfirmed = True
        self.user.confirmationToken = None
        self.user.save()
        return True
    
    def __generation_token(self) -> str:
        return str(uuid.uuid4())