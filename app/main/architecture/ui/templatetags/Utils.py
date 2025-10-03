from django import template

register = template.Library()

@register.filter
def get_dict_item(dictionary, key):
    """Filtre pour accéder aux éléments d'un dictionnaire par clé"""
    if dictionary and isinstance(dictionary, dict):
        return dictionary.get(key, [])
    return []    