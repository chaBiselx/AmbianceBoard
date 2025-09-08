from dataclasses import dataclass
from typing import Optional
from django.http import HttpRequest
from main.domain.common.enum.ModerationModelEnum import ModerationModelEnum


@dataclass
class TreatmentReportDto:
    """DTO pour les données de traitement des rapports de modération"""
    
    # Content Report fields
    content_report_accepted: Optional[str] = None
    content_report_id: Optional[str] = None
    content_moderator_response: Optional[str] = None
    
    # Moderator Log fields
    moderator_log_accepted: Optional[str] = None
    moderator_log_message: Optional[str] = None
    moderator_log_tag: Optional[str] = None
    moderator_log_model: str = ModerationModelEnum.UNKNOWN.name
    
    # Ban Action fields
    action_ban_user: Optional[str] = None
    action_ban_duration: str = '12'
    action_ban_reason: Optional[str] = None
    
    @classmethod
    def from_request(cls, request: HttpRequest) -> 'TreatmentReportDto':
        """Créer un DTO à partir d'une requête HTTP POST"""
        return cls(
            content_report_accepted=request.POST.get('contentReport_accepted'),
            content_report_id=request.POST.get('contentReport_id'),
            content_moderator_response=request.POST.get('content_moderator_response'),
            moderator_log_accepted=request.POST.get('moderator_log_accepted'),
            moderator_log_message=request.POST.get('moderator_log_message'),
            moderator_log_tag=request.POST.get('moderator_log_tag'),
            moderator_log_model=request.POST.get('moderator_log_model', ModerationModelEnum.UNKNOWN.name),
            action_ban_user=request.POST.get('action_ban_user'),
            action_ban_duration=request.POST.get('action_ban_duration', '12'),
            action_ban_reason=request.POST.get('action_ban_reason')
        )
