

from django import template
from main.models.UserModerationLog import UserModerationLog

register = template.Library()

@register.simple_tag
def get_user_logs(user):
    return UserModerationLog.objects.filter(user=user).order_by('created_at')[:10] 