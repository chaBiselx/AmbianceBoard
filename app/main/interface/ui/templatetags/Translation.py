from django import template
from django.utils.html import conditional_escape, mark_safe
from django.utils.translation import gettext


register = template.Library()


@register.simple_tag
def tkey(key: str, **context) -> str:
    message = gettext(key)
    if context:
        escaped_context = {
            name: conditional_escape(value)
            for name, value in context.items()
        }
        try:
            message = message % escaped_context
        except Exception:
            return mark_safe(message)

    return mark_safe(message)