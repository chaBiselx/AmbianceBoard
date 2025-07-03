from home.models.Tag import Tag
from django.db import models

class TagService:
    
    def __init__(self, request):
        self.request = request
    
    def get_tag_with_count(self):
        """
        Retourne la liste des tags avec le nombre de soundboard associés
        """
        tags = Tag.objects.filter(is_active=True).annotate(soundboard_count=models.Count('soundboards')).filter(soundboard_count__gt=0).order_by('-soundboard_count', 'name')
        return tags