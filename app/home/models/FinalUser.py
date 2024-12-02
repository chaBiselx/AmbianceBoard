import uuid 
from django.db import models

# Create your models here.

class FinalUser(models.Model):
    id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
    email = models.EmailField(max_length=254)
    userID = models.CharField(max_length=64, unique=True)
    
    def __str__(self):
        return self.id