from main.domain.common.utils.logger import LoggerFactory
import uuid
from main.architecture.persistence.models.ReportContent import ReportContent
from main.domain.common.exceptions.PostDataException import PostDataException
from main.domain.common.email.ModeratorEmail import ModeratorEmail
from main.domain.common.repository.ReportContentRepository import ReportContentRepository




class ReportContentService:
    
    def __init__(self, request):
        self.request = request
        self.logger = LoggerFactory.get_default_logger()
        
        
    def save_report(self):
        """Create a report for a playlist or soundboard if POST data is valid.

        Returns:
            ReportContent | None: The created report or None if invalid / error.
        """
        if self.request.method != 'POST':
            return None

        try:
            data = self._extract_post_data()
            self._validate_uuid(data['uuid_element'])
            if not self._is_valid_type(data['type_element'], data['uuid_element']):
                return None  # Error already logged in _is_valid_type
            report = self._create_report(**data)
            self._notify_moderators(report)
            return report
        except Exception as e:  # Keep broad catch to preserve original behavior
            self.logger.error(e)
            return None


    def _extract_post_data(self):
        return {
            'type_element': self.request.POST.get('element-type'),
            'uuid_element': self.request.POST.get('element-id'),
            'precision_element': self.request.POST.get('element-precision') or 'unknown',
            'description_element': self.request.POST.get('element-description') or ''
        }

    def _validate_uuid(self, uuid_element: str):
        try:
            uuid.UUID(uuid_element)
        except (ValueError, TypeError):
            raise PostDataException(f"Faux UUID de contenu {{uuid_element: {uuid_element}}}")

    def _is_valid_type(self, type_element: str, uuid_element: str) -> bool:
        if type_element and uuid_element and type_element in ['playlist', 'soundboard']:
            return True
        self.logger.error(
            PostDataException(
                f"Type de contenu ou uuid de contenu non renseigné {{type_element: {type_element}, uuid_element: {uuid_element}}}"
            )
        )
        return False

    def _create_report(self, type_element: str, uuid_element: str, precision_element: str, description_element: str):
        user = None
        if getattr(self.request, 'user', None) and self.request.user.is_authenticated:
            user = self.request.user
        return ReportContentRepository().create(
            type_element=type_element,
            uuid_element=uuid_element,
            precision_element=precision_element,
            description_element=description_element,
            creator=user
        )

    def _notify_moderators(self, report: ReportContent):
        try:
            ModeratorEmail().report_content_reported(report)
        except Exception as e:
            # Preserve original logging behavior
            self.logger.error(f"Erreur lors de l'envoi de l'email de signalement: {e}")
    
