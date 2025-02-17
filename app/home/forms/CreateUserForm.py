import re
from django import forms
from home.models.User import User

class CreateUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=64,label='Prénom', )
    last_name = forms.CharField(max_length=64,label='Nom de famille', )
    username = forms.CharField(max_length=64,label='Nom d’utilisateur', )
    email = forms.EmailField(max_length=69,label='Email', )
    password = forms.CharField(max_length=64,label='Mot de passe', widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=64,label='Confirmer le mot de passe', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas")

        # Définition des règles
        if len(password) < 8:
            raise forms.ValidationError(
                "Le mot de passe doit contenir au moins 8 caractères"
            )

        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError(
                "Le mot de passe doit contenir au moins une majuscule"
            )

        if not re.search(r'[a-z]', password):
            raise forms.ValidationError(
                "Le mot de passe doit contenir au moins une minuscule"
            )

        if not re.search(r'\d', password):
            raise forms.ValidationError(
                "Le mot de passe doit contenir au moins un chiffre"
            )

        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:"|,.<>/?]', password):
            raise forms.ValidationError(
                "Le mot de passe doit contenir au moins un caractère spécial"
            )

        email = cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé")

 

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
