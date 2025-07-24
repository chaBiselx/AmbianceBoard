from django import forms
from home.models.LinkMusic import LinkMusic

class LinkMusicForm(forms.ModelForm):
    class Meta:
        model = LinkMusic
        fields = ['url', 'alternativeName']
        widgets = {
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/music.mp3',
                'required': True
            }),
            'alternativeName': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom alternatif (optionnel)',
                'maxlength': 255
            })
        }
        labels = {
            'url': 'URL du lien musical',
            'alternativeName': 'Nom alternatif'
        }
        help_texts = {
            'url': 'Entrez l\'URL complète du fichier audio',
            'alternativeName': 'Nom à afficher à la place de l\'URL (optionnel)'
        }

    def clean_url(self):
        url = self.cleaned_data.get('url')
        if url:
            # Validation basique pour s'assurer que l'URL est valide
            if not url.startswith('https://'):
                raise forms.ValidationError("L'URL doit commencer par https://")
        return url

    def clean_alternativeName(self):
        alternative_name = self.cleaned_data.get('alternativeName')
        if alternative_name and len(alternative_name.strip()) == 0:
            return None
        return alternative_name