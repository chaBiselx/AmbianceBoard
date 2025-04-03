from django import forms
from home.models.PlaylistColorUser import PlaylistColorUser
from home.mixins.BootstrapFormMixin import BootstrapFormMixin

class PlaylistColorUserForm(BootstrapFormMixin, forms.Form):
    typePlaylist = forms.CharField()
    color = forms.CharField(max_length=7, widget=forms.TextInput(attrs={'type': 'color'}))
    colorText = forms.CharField(max_length=7, widget=forms.TextInput(attrs={'type': 'color'}))