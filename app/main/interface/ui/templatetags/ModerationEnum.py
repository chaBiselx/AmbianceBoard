from django import template
from main.domain.common.enum.ModerationEnum import ModerationEnum

register = template.Library()

@register.simple_tag
def list_values_report_moderation_enum():
    return [(item.value, item.name) for item in ModerationEnum]
