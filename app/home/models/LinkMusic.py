from django.db import models
from .Track import Track

class LinkMusic(Track):
    url = models.URLField(max_length=200)
    domained_name = models.CharField(max_length=255, blank=True)

    def get_name(self):
        return self.alternativeName if self.alternativeName else self.url
    
    def save(self, *args, **kwargs):
        if not self.domained_name:
            self.domained_name = self._extract_domain_from_url(self.url)
        super().save(*args, **kwargs)
        
    def _extract_domain_from_url(self, url: str) -> str:
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        return parsed_url.netloc if parsed_url.netloc else None
