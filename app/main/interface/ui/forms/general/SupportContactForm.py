from django import forms
from main.domain.common.mixins.BootstrapFormMixin import BootstrapFormMixin


class SupportContactForm(BootstrapFormMixin, forms.Form):
    website = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'class': 'visually-hidden',
            'tabindex': '-1',
            'autocomplete': 'off',
            'aria-hidden': 'true',
        }),
    )
    email = forms.EmailField(
        max_length=254,
        label='Email',
    )
    subject = forms.CharField(
        max_length=140,
        label='Sujet',
    )
    message = forms.CharField(
        max_length=4000,
        label='Message',
        widget=forms.Textarea(attrs={'rows': 8}),
    )
