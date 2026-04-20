from django import forms
from main.domain.common.mixins.BootstrapFormMixin import BootstrapFormMixin
from main.architecture.persistence.models.User import User
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.domain.common.enum.RecipientGroupEnum import RecipientGroupEnum


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].widget.attrs['class'] = self.fields['message'].widget.attrs.get('class', '') + ' editor-container'
        self.fields['message'].widget.attrs['data-editor'] = 'simple'

    def clean(self):
        cleaned_data = super().clean()
        group = cleaned_data.get('recipient_group')
        recipients = cleaned_data.get('recipients')

        if not group and not recipients:
            raise forms.ValidationError(
                'Veuillez sélectionner un groupe de destinataires ou choisir des utilisateurs manuellement.'
            )

        if group:
            resolved = self._resolve_group(group)
            if not resolved.exists():
                raise forms.ValidationError('Aucun utilisateur trouvé pour ce groupe.')
            cleaned_data['recipients'] = resolved

        if cleaned_data.get('recipients'):
            for user in cleaned_data['recipients']:
                if not user.email:
                    raise forms.ValidationError(f"L'utilisateur {user.username} n'a pas d'adresse email.")

        return cleaned_data

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
