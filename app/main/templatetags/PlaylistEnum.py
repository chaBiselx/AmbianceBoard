from django import template
from main.enum.PlaylistTypeEnum import PlaylistTypeEnum

register = template.Library()

@register.filter
def to_value(name):
    return PlaylistTypeEnum[name].value

