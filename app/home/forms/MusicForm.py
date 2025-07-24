from django import forms
from home.models.Music import Music
from home.mixins.BootstrapFormMixin import BootstrapFormMixin
from home.enum.MusicFormatEnum import MusicFormatEnum

class MusicForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Music
        fields = ('file', 'alternativeName' )
    
    file = forms.FileField(
        label='Fichier de musique', 
        widget=forms.FileInput(attrs={'accept': ','.join(MusicFormatEnum.values())}),
    )
        
    def clean_file(self):
        file = self.cleaned_data['file']
        allowed_extensions = MusicFormatEnum.values()  # Convert enum values to
        if file and not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
             raise forms.ValidationError(f'Seuls les fichiers {", ".join(allowed_extensions)} sont autorisés.')
        return file