from django import forms
from main.architecture.persistence.models.User import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from main.domain.common.mixins.BootstrapFormMixin import BootstrapFormMixin
from main.domain.common.repository.UserRepository import UserRepository


class UserResetPasswordForm(BootstrapFormMixin, forms.Form):
    identifier = forms.CharField(
        label="Identifiant ou Email",
        max_length=150,
        required=True
    )

    def clean_identifier(self):
        value = self.cleaned_data["identifier"]

        # Vérifier si c'est une adresse e-mail
        try:
            validate_email(value)  # Vérifie la structure de l'e-mail
            user = UserRepository().get_user_by_email(value)
        except ValidationError:
            # Ce n'est pas un email valide, donc on cherche par username
            user = UserRepository().get_user_by_username(value)

        if not user:
            raise ValidationError("Aucun utilisateur trouvé avec cet identifiant ou email.")

        return user 