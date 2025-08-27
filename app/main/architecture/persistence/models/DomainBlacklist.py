from django.db import models

class DomainBlacklist(models.Model):
    """
    Modèle représentant une liste noire de domaines.

    Permet de bloquer certains domaines lors de la création de compte.
    afin de prevenir les faux comptes et les abus.
    """
    
    domain = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
        Représentation textuelle du domaine blacklisté.
        
        Returns:
            str: Nom du domaine
        """
        return self.domain

    class Meta:
        verbose_name = "Blacklisted Domain"
        verbose_name_plural = "Blacklisted Domains"
