from django import forms
from main.domain.common.mixins.BootstrapFormMixin import BootstrapFormMixin
from main.architecture.persistence.models.User import User
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.domain.common.enum.RecipientGroupEnum import RecipientGroupEnum
from main.interface.ui.forms.manager.ManagerEmailValidationUtils import ManagerEmailValidationUtils


class ManagerSendEmailForm(BootstrapFormMixin, forms.Form):
    """
    Formulaire pour envoyer un email à un ou plusieurs utilisateurs.
    """

    recipient_group = forms.ChoiceField(
        choices=RecipientGroupEnum.get_form_choices(),
        label='Groupe de destinataires',
        required=False,
        widget=forms.Select(),
        help_text='Sélectionnez un groupe prédéfini ou choisissez manuellement ci-dessous.',
    )

    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True, isBan=False).order_by('username'),
        label='Destinataires',
        required=False,
        widget=forms.SelectMultiple(attrs={
            'size': '10',
        }),
        help_text='Maintenez Ctrl (ou Cmd) pour sélectionner plusieurs utilisateurs.',
    )

    subject = forms.CharField(
        max_length=255,
        label='Sujet',
        widget=forms.TextInput(attrs={
            'placeholder': 'Sujet du mail',
        }),
    )

    message = forms.CharField(
        label='Message',
        widget=forms.Textarea(attrs={
            'rows': 8,
            'placeholder': 'Contenu du mail',
        }),
    )

    external_emails = forms.CharField(
        label='Emails externes',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'exemple@domaine.fr, autre@domaine.fr',
        }),
        help_text='Ajoutez des emails séparés par des virgules, points-virgules, espaces ou retours à la ligne.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].widget.attrs['class'] = self.fields['message'].widget.attrs.get('class', '') + ' editor-container'
        self.fields['message'].widget.attrs['data-editor'] = 'simple'

    def clean(self):
        cleaned_data = super().clean()
        group = cleaned_data.get('recipient_group')
        recipients = cleaned_data.get('recipients')
        external_emails = ManagerEmailValidationUtils.parse_and_validate_external_emails(
            cleaned_data.get('external_emails')
        )
        cleaned_data['external_emails'] = external_emails

        self._validate_recipient_source(group, recipients, external_emails)
        cleaned_data['recipients'] = self._resolve_recipients(group, recipients)
        self._validate_recipients_have_email(cleaned_data['recipients'])
        cleaned_data['external_emails'] = self._remove_duplicate_external_emails(
            cleaned_data['recipients'],
            cleaned_data['external_emails'],
        )

        return cleaned_data

    @staticmethod
    def _validate_recipient_source(group, recipients, external_emails: list[str]) -> None:
        if not group and not recipients and not external_emails:
            raise forms.ValidationError(
                'Veuillez sélectionner un groupe de destinataires, choisir des utilisateurs manuellement ou renseigner des emails externes.'
            )

    def _resolve_recipients(self, group: str, recipients):
        if not group:
            return recipients

        resolved = self._resolve_group(group)
        if not resolved.exists():
            raise forms.ValidationError('Aucun utilisateur trouvé pour ce groupe.')
        return resolved

    @staticmethod
    def _validate_recipients_have_email(recipients) -> None:
        if not recipients:
            return

        for user in recipients:
            if not user.email:
                raise forms.ValidationError(f"L'utilisateur {user.username} n'a pas d'adresse email.")

    @staticmethod
    def _remove_duplicate_external_emails(recipients, external_emails: list[str]) -> list[str]:
        if not recipients or not external_emails:
            return external_emails

        existing_recipients = {user.email.lower() for user in recipients if user.email}
        return [
            email for email in external_emails if email.lower() not in existing_recipients
        ]

    @staticmethod
    def _resolve_group(group: str):
        base_qs = User.objects.filter(is_active=True).exclude(email='')
        if group == RecipientGroupEnum.ALL.name.lower(): # Inclut tous les utilisateurs actifs avec une adresse email
            return base_qs
        elif group == RecipientGroupEnum.NON_MANAGER.name.lower(): # Inclut tous les utilisateurs sauf les managers
            return base_qs.exclude(
                user_permissions__codename=PermissionEnum.MANAGER_EXECUTE_BATCHS.value
            )
        elif group == RecipientGroupEnum.BASIC.name.lower(): # Inclut les utilisateurs standards, mais exclut les modérateurs et managers
            excluded_user_ids = User.objects.filter(
                user_permissions__codename__in=[
                    PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.value,
                    PermissionEnum.MANAGER_EXECUTE_BATCHS.value,
                ]
            ).values('pk')
            return base_qs.filter(
                user_permissions__codename=PermissionEnum.USER_STANDARD.value
            ).exclude(
                pk__in=excluded_user_ids
            ).distinct()
        return base_qs.none()
