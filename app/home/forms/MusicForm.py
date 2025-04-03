from django import forms
from home.models.Music import Music
from home.mixins.BootstrapFormMixin import BootstrapFormMixin

class MusicForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Music
        fields = ('file', 'alternativeName' )
    
    file = forms.FileField(
        label='Fichier de musique', 
        widget=forms.FileInput(attrs={'accept': '.mp3,.wav,.ogg'}),
    )
        
    def clean_file(self):
        file = self.cleaned_data['file']
        allowed_extensions = ['.mp3', '.wav', '.ogg']
        if file and not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
             raise forms.ValidationError('Seuls les fichiers MP3, WAV et OGG sont autorisés.')
        return file