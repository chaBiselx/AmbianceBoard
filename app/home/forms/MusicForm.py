from django import forms
from ..models.Music import Music

class MusicForm(forms.ModelForm):
    class Meta:
        model = Music
        fields = ('file', 'alternativeName' )