from django import template

register = template.Library()

@register.filter
def applys_boostrap_class(tag):
    bootstrap_classes = {
        'success': 'success',
        'info': 'info',
        'warning': 'warning',
        'error': 'danger',
    }
    return bootstrap_classes.get(
        tag,
        'info' 
    )