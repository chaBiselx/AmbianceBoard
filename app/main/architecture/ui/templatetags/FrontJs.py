from django import template
from main.domain.common.utils.settings import Settings
from main.architecture.ui.service.StaticFilesService import StaticFilesService
import os

register = template.Library()

@register.filter
def search_true_file(name_file):
    name_file = name_file.strip()
    static_root = Settings.get('STATIC_PRIMARY_DIR')
    js_dir = os.path.join(static_root, 'js')
    
    static_files_service = StaticFilesService(js_dir)
    return 'js/' + static_files_service.search(name_file)
    
    