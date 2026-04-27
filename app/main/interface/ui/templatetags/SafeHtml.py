from django import template
from django.utils.safestring import mark_safe
import bleach

register = template.Library()

# Liste des balises HTML autorisées
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'b', 'i', 'u', 
    'a', 'img', 'ul', 'ol', 'li', 'span', 'div',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
]

# Attributs autorisés par balise
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height'],
    'span': ['class'],
    'div': ['class'],
}

# Protocoles autorisés pour les liens
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


@register.filter(name='safe_html')
def safe_html(value):
    """
    Nettoie le HTML en supprimant les balises et attributs dangereux
    pour éviter les attaques XSS tout en conservant le formatage de base.
    
    Usage dans les templates:
        {{ notification.message|safe_html }}
        {{ notification.message|truncatewords:10|safe_html }}
    """
    if not value:
        return ''
    
    # Nettoie le HTML avec bleach
    cleaned = bleach.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True  # Supprime les balises non autorisées au lieu de les échapper
    )
    
    # Marque comme safe pour Django (le contenu a été nettoyé)
    return mark_safe(cleaned)

