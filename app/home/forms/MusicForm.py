from django import forms
from ..models.Music import Music

class MusicForm(forms.ModelForm):
    class Meta:
        model = Music
        fields = ('file', 'alternativeName' )
        
    def clean_file(self):
        file = self.cleaned_data['file']
        if file and  not file.name.endswith(('.mp3', '.wav', '.ogg')):
                raise forms.ValidationError('Seuls les fichiers MP3, WAV et OGG sont autorisés.')
        return file