from main.domain.common.utils.settings import Settings
from main.domain.common.utils.EmailSender import EmailSender
from main.domain.general.dto.SupportContactDto import SupportContactDto


class SupportContactService:
    """Service d'envoi des messages de support depuis la page de contact."""

    def send(self, payload: SupportContactDto) -> bool:
        body = (
            "Nouveau message support depuis la page de contact AmbianceBoard.\n\n"
            f"Email: {payload.email}\n"
            f"Sujet: {payload.subject}\n\n"
            f"Message:\n{payload.message}\n"
        )

        return EmailSender().send_email(
            subject=f"[Support public] {payload.subject}",
            body=body,
            from_email=payload.email,
            to_emails=[Settings.get('EMAIL_CONTACT')],
            is_html=False,
        )
