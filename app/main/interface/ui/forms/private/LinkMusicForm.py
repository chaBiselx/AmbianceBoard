from django import forms
from django.utils.safestring import mark_safe
from main.architecture.persistence.models.LinkMusic import LinkMusic

REQUIRED_URL_PREFIX = 'https://'
EXAMPLE_MUSIC_URL = 'https://example.com/music.mp3'
EXAMPLE_STREAM_URL = 'https://hemnos.cdnstream.com/1881_128'
EXAMPLE_YOUTUBE_URL = 'https://www.youtube.com/watch?v=HJR54LOaDbo&list=RDHJR54LOaDbo'


def _generate_tooltip_html():
    return mark_safe(
        (
            'Liste des liens compatible : '
            '<dl>'
            f'<dt>Exemple musique :</dt><dd><small>{EXAMPLE_MUSIC_URL}</small></dd>'
            f'<dt>Exemple stream :</dt><dd><small>{EXAMPLE_STREAM_URL}</small></dd>'
            f'<dt>Exemple YouTube :</dt><dd><small>{EXAMPLE_YOUTUBE_URL}</small></dd>'
            '</dl>'
        )
    )


def _url_label_with_tooltip():
    return mark_safe(
        'URL du lien musical '
        '<span class="badge rounded-pill bg-primary" '
        'data-bs-toggle="tooltip" data-bs-html="true" data-bs-placement="bottom" '
        f'title="{_generate_tooltip_html()}">'
        '<i class="fa-solid fa-info"></i>'
        '</span>'
    )



class LinkMusicForm(forms.ModelForm):
    class Meta:
        model = LinkMusic
        fields = ['url', 'alternativeName']
        widgets = {
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': EXAMPLE_MUSIC_URL,
                'required': True
            }),
            'alternativeName': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom alternatif (optionnel)',
                'maxlength': 255
            })
        }
        labels = {
            'url': _url_label_with_tooltip(),
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
            if not url.startswith(REQUIRED_URL_PREFIX):
                raise forms.ValidationError("L'URL doit commencer par https://")
        return url

    def clean_alternativeName(self):
        alternative_name = self.cleaned_data.get('alternativeName')
        if alternative_name and len(alternative_name.strip()) == 0:
            return None
        return alternative_name