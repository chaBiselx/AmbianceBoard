from django import template
from home.enum.ReportContentResultEnum import ReportContentResultEnum

register = template.Library()

@register.simple_tag
def list_values_report_content_result_enum():
    return [(item.value, item.name) for item in ReportContentResultEnum]
