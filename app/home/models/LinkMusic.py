from django.db import models
from .Track import Track
from home.enum.LinkMusicTypeEnum import LinkMusicTypeEnum

class LinkMusic(Track):
    """
    Modèle représentant un lien vers un contenu audio externe.
    
    Hérite de Track et permet de référencer des contenus audio
    via des URLs externes (streaming, fichiers distants, etc.).
    Le domaine est automatiquement extrait de l'URL pour faciliter la modération.
    """
    
    url = models.URLField(max_length=200)
    domained_name = models.CharField(max_length=255, blank=True)
    urlType = models.CharField(max_length=50, blank=True, choices=[
        (LinkMusicTypeEnum.FILE.name, LinkMusicTypeEnum.FILE.value),
        (LinkMusicTypeEnum.STREAM.name, LinkMusicTypeEnum.STREAM.value),
        (LinkMusicTypeEnum.OTHER.name, LinkMusicTypeEnum.OTHER.value),
        (LinkMusicTypeEnum.ERROR.name, LinkMusicTypeEnum.ERROR.value),
    ])

    def get_name(self) -> str:
        """
        Récupère le nom d'affichage du lien musical.
        
        Returns:
            str: Le nom alternatif s'il existe, sinon l'URL
        """
        return self.alternativeName if self.alternativeName else self.url
    
    def save(self, *args, **kwargs) -> None:
        """
        Sauvegarde le lien musical avec extraction automatique du domaine.
        
        Args:
            *args: Arguments positionnels pour la méthode save
            **kwargs: Arguments nommés pour la méthode save
        """
        if not self.domained_name:
            self.domained_name = self._extract_domain_from_url(self.url)
        super().save(*args, **kwargs)
        
    def _extract_domain_from_url(self, url: str) -> str:
        """
        Extrait le nom de domaine d'une URL.
        
        Args:
            url (str): URL dont extraire le domaine
            
        Returns:
            str: Nom de domaine ou None si extraction impossible
        """
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        return parsed_url.netloc if parsed_url.netloc else None
