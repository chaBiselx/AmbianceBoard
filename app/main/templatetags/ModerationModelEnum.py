from django import template
from main.enum.ModerationModelEnum import ModerationModelEnum

register = template.Library()

@register.simple_tag
def list_values_report_moderation__model_enum():
    return [(item.value, item.name) for item in ModerationModelEnum]
