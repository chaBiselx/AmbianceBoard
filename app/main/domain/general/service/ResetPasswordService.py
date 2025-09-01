from main.architecture.persistence.models.User import User
import hashlib
import secrets
from django.utils import timezone
from django.urls import reverse
from main.domain.common.exceptions.SecurityException import SecurityException
from main.domain.common.utils.logger import logger



class ResetPasswordService():
    
    def __init__(self, user:User):
        self.user = user
    
    def generation_uri(self):
        self.user.tokenReinitialisation = self.__generation_token()
        self.user.demandeTokenDate = timezone.now()
        self.user.save()
        return reverse("token_validation_reset_password", kwargs={'uuid_user': self.user.uuid, 'token_reinitialisation': self.user.tokenReinitialisation })
        
    def verification_token(self, token_reinitialisation:str) -> bool : 
        if self.user is None : 
            raise SecurityException("User not found")
        if self.user.tokenReinitialisation is None :
            raise SecurityException("Reinit token not found")
        if token_reinitialisation is None :
            raise SecurityException("token invalid")
        if self.user.get_reinitialisation_token() != str(token_reinitialisation):
            raise SecurityException("Reinit token dont match")
        if self.user.demandeTokenDate is None:
            raise SecurityException("Reinit date not found")
        if self.user.demandeTokenDate + timezone.timedelta(days=1) < timezone.now():
            raise SecurityException("Reinit date expired")
                
        return True
    
    def clean(self):
        self.user.tokenReinitialisation = None
        self.user.demandeTokenDate = None
        self.user.save()
        return self

               

    def __generation_token(self) -> str : 
        input_data = str(secrets.randbits(64))
        salt = secrets.token_hex(8)
        combined = f"{salt}{input_data}"
        logger.debug(combined)
        logger.debug(combined.encode())
        logger.debug(hashlib.sha256(combined.encode()))
        logger.debug(hashlib.sha256(combined.encode()).hexdigest())
        return hashlib.sha256(combined.encode()).hexdigest()
