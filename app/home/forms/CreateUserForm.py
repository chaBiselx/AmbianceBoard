import re
from django import forms
from home.models.User import User
from home.forms.UserPasswordForm import UserPasswordForm

class CreateUserForm(UserPasswordForm):
    first_name = forms.CharField(max_length=64,label='Prénom', )
    last_name = forms.CharField(max_length=64,label='Nom de famille', )
    username = forms.CharField(max_length=64,label='Nom d’utilisateur', )
    email = forms.EmailField(max_length=69,label='Email', )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        protected_names = [
            'root', 'admin', 'administrator', 'superuser', 'sysadmin', 'webmaster',
            'support', 'postmaster', 'hostmaster', 'abuse', 'noreply', 'security',
            'test', 'guest', 'info', 'contact', 'help', 'www', 'ftp', 'mail',
            'news', 'uucp', 'operator', 'staff', 'user', 'users', 'system'
        ]
        if username.lower() in protected_names:
            raise forms.ValidationError("Ce nom d'utilisateur est protégé et ne peut pas être utilisé.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
