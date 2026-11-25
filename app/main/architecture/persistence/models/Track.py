from django.db import models
from .Playlist import Playlist
from django.http import StreamingHttpResponse
from main.domain.common.strategy.urlMusicStreamStrategy import UrlMusicStreamStrategy
from main.domain.common.strategy.urlMusicStream.FileStreamExtract import FileStreamExtract
from django.shortcuts import redirect
from main.domain.common.utils.AudioDurationUtils import AudioDurationUtils

AUDIO_CONTENT_TYPE = 'audio/*'


class Track(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    alternativeName = models.CharField(max_length=255, default=None,  blank=True)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, null=False, blank=False, related_name="tracks")
    duration = models.FloatField(null=True, blank=True)  # Durée en secondes

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
    
    def get_source(self):
        """
        Retourne la source de la musique ou du lien.
        """
        if self.is_music():
            return self.music.file
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
    
    def get_download_url(self):
        """
        Retourne l'URL de téléchargement pour la musique ou le lien.
        """
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
    
    def get_reponse_content(self, range_header=None):
        if self.is_music():
            return self._get_music_file_response(range_header)
        if self.is_link_music():
            return self._get_link_response(range_header)
        return None

    def _get_music_file_response(self, range_header):
        audio_file = self.music.file
        file_size = audio_file.size
        byte_range = self._parse_byte_range(range_header, file_size)
        if byte_range == (-1, -1):
            response = StreamingHttpResponse(status=416, content_type=AUDIO_CONTENT_TYPE)
            response['Content-Range'] = f'bytes */{file_size}'
            response['Accept-Ranges'] = 'bytes'
            return response

        if byte_range:
            response = self._create_partial_file_response(audio_file, byte_range, file_size)
        else:
            response = StreamingHttpResponse(audio_file, content_type=AUDIO_CONTENT_TYPE)
            response['Content-Length'] = str(file_size)

        response['Accept-Ranges'] = 'bytes'
        response['Content-Disposition'] = 'inline; filename="{}"'.format(self.music.fileName)
        return response

    def _create_partial_file_response(self, audio_file, byte_range, file_size):
        start, end = byte_range
        audio_file.open('rb')
        audio_file.seek(start)

        def content():
            remaining = end - start + 1
            try:
                while remaining > 0:
                    chunk = audio_file.read(min(8192, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk
            finally:
                audio_file.close()

        response = StreamingHttpResponse(content(), status=206, content_type=AUDIO_CONTENT_TYPE)
        response['Content-Length'] = str(end - start + 1)
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        return response

    def _get_link_response(self, range_header):
        strategy_class = UrlMusicStreamStrategy().get_strategy(self.linkmusic)
        if not strategy_class:
            raise ValueError(f"Aucune stratégie trouvée pour le domaine: {self.linkmusic.domained_name}")

        strategy_instance = strategy_class(self.linkmusic)
        if isinstance(strategy_instance, FileStreamExtract):
            stream, type_stream = strategy_instance.extract(range_header)
        else:
            stream, type_stream = strategy_instance.extract()
        if type_stream == 'file':
            upstream_response = strategy_instance.response
            response = StreamingHttpResponse(
                stream,
                status=upstream_response.status_code,
                content_type=upstream_response.headers.get('Content-Type', AUDIO_CONTENT_TYPE),
            )
            for header in ('Accept-Ranges', 'Content-Length', 'Content-Range'):
                if header in upstream_response.headers:
                    response[header] = upstream_response.headers[header]
            response['Content-Disposition'] = 'inline; filename="{}"'.format(self.get_name())
            return response
        if type_stream == 'redirect':
            return redirect(self.linkmusic.url, permanent=False)
        raise ValueError("Aucun stream audio trouvé pour le lien")

    @staticmethod
    def _parse_byte_range(range_header, file_size):
        if not range_header or not range_header.startswith('bytes=') or ',' in range_header:
            return None

        range_start, separator, range_end = range_header[6:].partition('-')
        if not separator or (not range_start and not range_end):
            return None

        try:
            if range_start:
                start = int(range_start)
                end = int(range_end) if range_end else file_size - 1
            else:
                suffix_length = int(range_end)
                if suffix_length <= 0:
                    return (-1, -1)
                start = max(file_size - suffix_length, 0)
                end = file_size - 1
        except ValueError:
            return None

        if start < 0 or start >= file_size or end < start:
            return (-1, -1)
        return start, min(end, file_size - 1)
    
    def get_duration(self):
        """
        Retourne la durée de l'audio en secondes.
        
        Pour les fichiers Music locaux, utilise les métadonnées audio pour extraire la durée.
        Pour les LinkMusic, retourne None car il faudrait télécharger le fichier.
        
        Returns:
            float: La durée en secondes, ou None si impossible à déterminer
        """
        if self.duration is not None:
            return self.duration

        if self.is_music():
            self.duration = AudioDurationUtils.get_duration_from_file(self.music.file.path)
            if(self.duration is not None):
                self.save(update_fields=['duration'])
                return self.duration
        if self.is_link_music() and self.linkmusic.urlType == 'FILE':
            self.duration = AudioDurationUtils.get_duration_from_url_file(self.linkmusic.url)
            if(self.duration is not None):
                self.save(update_fields=['duration'])
                return self.duration
        return None

    def __str__(self):
        return self.get_name()
