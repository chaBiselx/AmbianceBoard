from django import forms
from main.models.User import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from main.domain.common.mixins.BootstrapFormMixin import BootstrapFormMixin


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
            user = User.objects.filter(email=value).first()
        except ValidationError:
            # Ce n'est pas un email valide, donc on cherche par username
            user = User.objects.filter(username=value).first()

        if not user:
            raise ValidationError("Aucun utilisateur trouvé avec cet identifiant ou email.")

        return user 