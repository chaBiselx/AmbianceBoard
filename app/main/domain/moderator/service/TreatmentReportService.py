from typing import Optional

from main.domain.common.repository.ReportContentRepository import ReportContentRepository
from main.domain.common.repository.UserModerationLogRepository import UserModerationLogRepository
from main.domain.common.enum.ModerationModelEnum import ModerationModelEnum
from main.domain.moderator.dto.TreatmentReportDto import TreatmentReportDto

from main.architecture.persistence.models.User import User
from datetime import datetime, timedelta


class TreatmentReportService:
    report_content = None

    def __init__(self, dto: TreatmentReportDto, user: User, moderator: User) -> None:
        self.user = user
        self.moderator = moderator
        self.dto = dto
        self.report_repository = ReportContentRepository()
        self.user_moderation_log_repository = UserModerationLogRepository()

    def update_content_report(self):
        if self.dto.content_report_accepted:
            if self.dto.content_report_id and self.dto.content_moderator_response:
                self.report_content = self.report_repository.get(self.dto.content_report_id)
                if self.report_content is not None:
                    self.report_content.resultModerator = self.dto.content_moderator_response
                    self.report_content.moderator = self.moderator
                    self.report_content.dateResultModerator = datetime.now()
                    self.report_content.save()
    
    def create_log_moderation(self):
        if self.dto.moderator_log_accepted:
            self.user_moderation_log_repository.create(
                {
                    'user': self.user,
                    'moderator': self.moderator,
                    'message': self.dto.moderator_log_message,
                    'tag': self.dto.moderator_log_tag,
                    'model': self.dto.moderator_log_model,
                    'report': self.report_content
                }
            )
          
            
    def action_ban(self):
        if self.dto.action_ban_user:
            duration_ban = int(self.dto.action_ban_duration)
            if duration_ban <= 0:
                duration_ban = 12
            self.user.isBan = True
            self.user.reasonBan = self.dto.action_ban_reason
            self.user.banExpiration = datetime.now() + timedelta(days=duration_ban * 31)
            self.user.save()

