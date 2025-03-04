from django import template
from home.enum.PlaylistTypeEnum import PlaylistTypeEnum

register = template.Library()

@register.filter
def to_value(name):
    return PlaylistTypeEnum[name].value

