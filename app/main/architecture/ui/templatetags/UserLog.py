

from django import template
from main.domain.common.repository.UserModerationLogRepository import UserModerationLogRepository

register = template.Library()

@register.simple_tag
def get_user_logs(user):
    return UserModerationLogRepository().get_resume_moderation(user)