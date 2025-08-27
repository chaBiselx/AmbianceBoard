from django import template
from main.utils.settings import Settings
from main.service.utils.StaticFilesService import StaticFilesService
import os

register = template.Library()

@register.filter
def search_true_file(name_file):
    name_file = name_file.strip()
    static_root = Settings.get('STATICFILES_DIRS')[0]
    js_dir = os.path.join(static_root, 'js')
    
    static_files_service = StaticFilesService(js_dir)
    return 'js/' + static_files_service.search(name_file)
    
    