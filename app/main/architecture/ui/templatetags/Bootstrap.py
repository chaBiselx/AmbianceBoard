from django import template
import re

register = template.Library()

@register.filter
def applys_boostrap_class(tag):
    """Nettoie la valeur du tag (suppression d'un éventuel bloc JSON / bruit)
    puis renvoie la classe Bootstrap correspondante.

    Ex: '{"code": "WEBKIT_LIMITATION"} warning' -> 'warning' -> 'warning'
    """
    if not isinstance(tag, str):
        return 'info'


    cleaned = re.sub(r'^\s*\{.*?\}\s*', '', tag).strip()
    cleaned = re.sub(r'\s+', '', cleaned)

    cleaned = cleaned.lower()

    bootstrap_classes = {
        'success': 'success',
        'info': 'info',
        'warning': 'warning',
        'error': 'danger',
    }

    return bootstrap_classes.get(cleaned, 'info')