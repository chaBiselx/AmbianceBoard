from django import forms
from ..models.SoundBoard import SoundBoard

class SoundBoardForm(forms.ModelForm):
    class Meta:
        model = SoundBoard
        fields = ('name', 'color', 'colorText')