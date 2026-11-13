from main.domain.common.utils.EmailSender import EmailSender
from main.domain.common.utils.settings import Settings


class TrackLabelReportEmail:
    """Envoie au support les signalements de labels de piste."""

    def send_report(self, track, labels, reporter) -> bool:
        contact_email = Settings.get('EMAIL_CONTACT')
        if not contact_email:
            raise ValueError('EMAIL_CONTACT is not configured')

        incorrect_labels = '\n'.join(
            f'- {label.category}: {label.label} ({label.confidence:.0%})'
            for label in labels
        )
        body = (
            'Un utilisateur signale des labels incorrects.\n\n'
            f'Piste: {track.get_name()} (ID: {track.id})\n'
            f'Playlist: {track.playlist.name} (UUID: {track.playlist.uuid})\n\n'
            'Déclarant:\n'
            f'Username: {reporter.username}\n'
            f'UUID: {reporter.uuid}\n'
            f'Email: {reporter.email or "non renseigné"}\n\n'
            f'Labels signalés:\n{incorrect_labels}\n'
        )

        return EmailSender().send_email(
            subject=f'[Signalement labels] {track.get_name()}',
            body=body,
            from_email=contact_email,
            to_emails=[contact_email],
            reply_to_email=reporter.email or None,
            is_html=False,
        )