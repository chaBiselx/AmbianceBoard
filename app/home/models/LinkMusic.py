from django.db import models
from .Track import Track

class LinkMusic(Track):
    url = models.URLField(max_length=200)

    def get_name(self):
        return self.alternativeName if self.alternativeName else self.url
