from django.db import models
from .Playlist import Playlist
from django.http import  HttpResponse


class Track(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    alternativeName = models.CharField(max_length=255, default=None, null=True, blank=True)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, null=False, blank=False, related_name="tracks")

    class Meta:
        abstract = False
        
    def is_music(self):
        """
        Vérifie si l'instance est une musique.
        """
        return hasattr(self, 'music')
    
    def is_link_music(self):
        """
        Vérifie si l'instance est un lien de musique.
        """
        return hasattr(self, 'linkmusic')
    
    def get_source(self):
        """
        Retourne la source de la musique ou du lien.
        """
        if self.is_music():
            return self.music.fileName
        if self.is_link_music():
            return self.linkmusic.url
        # Fallback pour les instances de Track qui ne seraient ni l'un ni l'autre
        return "unknown"

    def get_name(self):
        if self.is_music():
            return self.music.get_name()
        if self.is_link_music():
            return self.linkmusic.get_name()
        # Fallback pour les instances de Track qui ne seraient ni l'un ni l'autre
        return self.alternativeName or "Track sans nom"
    
    def get_url(self):
        if self.is_music():
            return self.music.file.url
        if self.is_link_music():
            return self.linkmusic.url
        # Fallback pour les instances de Track qui ne seraient ni l'un ni l'autre
        return None
    
    def get_stream_url(self):
        """
        Retourne l'URL de streaming pour la musique ou le lien.
        Si la musique est un fichier, retourne son URL.
        Si c'est un lien, retourne l'URL du lien.
        """
        if self.is_music():
            return self.music.file.url
        if self.is_link_music():
            return self.linkmusic.url
        # Fallback pour les instances de Track qui ne seraient ni l'un ni l'autre
        return None
    
    def get_reponse_content(self):
        if self.is_music():
            response = HttpResponse(self.get_stream_url(), content_type='audio/*')
            response['Content-Disposition'] = 'inline; filename="{}"'.format(self.music.fileName)
            return response
        if self.is_link_music():
            pass
            # response = HttpResponse(linkmusic.file, content_type='audio/*')
            # response['Content-Disposition'] = 'inline; filename="{}"'.format(linkmusic.fileName)
        # Fallback pour les instances de Track qui ne seraient ni l'un ni l'autre
        return None

    def __str__(self):
        return self.get_name()
