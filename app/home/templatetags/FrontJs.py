from django import template
from django.conf import settings
import os
import re

register = template.Library()

@register.filter
def search_true_file(name_file):
    name_file = name_file.strip()
    static_root = settings.STATICFILES_DIRS[0]
    js_dir = os.path.join(static_root, 'js')
    files = os.listdir(js_dir)

    js_files = [f for f in files if re.match(rf"{name_file}\.[a-zA-Z0-9]+\.js", f)]
    return 'js/' + js_files[0] if js_files else None
    