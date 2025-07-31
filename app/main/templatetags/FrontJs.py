from django import template
from django.conf import settings
from main.service.utils.StaticFilesService import StaticFilesService
import os

register = template.Library()

@register.filter
def search_true_file(name_file):
    name_file = name_file.strip()
    static_root = settings.STATICFILES_DIRS[0]
    js_dir = os.path.join(static_root, 'js')
    
    static_files_service = StaticFilesService(js_dir)
    return 'js/' + static_files_service.search(name_file)
    
    