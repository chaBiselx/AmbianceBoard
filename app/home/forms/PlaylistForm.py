from django import forms
from home.models.Playlist import Playlist
from home.mixins.BootstrapFormMixin import BootstrapFormMixin



class PlaylistForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ('name', 'typePlaylist', 'useSpecificColor', 'color', 'colorText', 'volume', 'icon', 'maxDelay')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Supprime le lien si un fichier existe
        if self.instance and self.instance.icon:
            self.fields['icon'].widget.attrs.update({'placeholder': 'Choisissez un nouveau fichier'})
            self.fields['icon'].help_text = f"Image déja choisie <a id='id_icon_alreadyexist' href='{ self.instance.icon.url }' target='_blank'>Voir</a>" 
        
        
    name = forms.CharField(
        label='Nom de la playlist', 
        max_length=255, 
        required=True
    )
    typePlaylist = forms.ChoiceField(
        label='Type de playlist',
        choices=Playlist.typePlaylist.field.choices,
        required=True,
    )
    useSpecificColor = forms.BooleanField(required=False, label='Utiliser une couleur personnalisée', initial=False)
    color = forms.CharField(
        label='Couleur du background',
        widget=forms.TextInput(attrs={'type': 'color', 'typeInput': 'color'}),
        initial="#000000"
    )
    colorText = forms.CharField(
        label='Couleur du texte',
        widget=forms.TextInput(attrs={'type': 'color', 'typeInput': 'color'}),
        initial="#ffffff"
    )
    volume = forms.IntegerField(
        label='Volume',
        min_value=0,
        max_value=100,
        initial=75,
        widget=forms.NumberInput(attrs={'type': 'range', 'min': 0, 'max': 100, 'typeInput': 'range'})
    )
    icon = forms.FileField(
        label='Icone de la playlist', 
        widget=forms.FileInput(attrs={'accept': '.jpg, .jpeg, .jfif, .pjpeg, .pjp, .png, .svg, .webp'}),
        required=False
    )
    clear_icon = forms.BooleanField(required=False, label='Supprimer le fichier', initial=False)
    useSpecificDelay = forms.BooleanField(required=False, label='Utiliser un delai aléatoire spécifique', initial=False)
    maxDelay = forms.IntegerField(
        label='Délai maximum (en seconde) avant de jouer la musique suivante',
        min_value=0,
        max_value=3600,
        initial=0
    )
    def clean_icon(self):
        if self.cleaned_data.get('clear_icon'):
            return None
        icon = self.cleaned_data['icon']
        allowed_extensions = [".jpg" , ".jpeg" , ".jfif" , ".pjpeg" , ".pjp", ".png", ".svg", ".webp"]
        if icon and not any(icon.name.lower().endswith(ext) for ext in allowed_extensions):
             raise forms.ValidationError('Seuls les fichiers audio (.mp3, .wav, .ogg) sont autorisés.')
        return icon
    
    def save(self, commit=True):
        instance = super().save(commit=False)

        # Si le fichier doit être supprimé, on l'initialise à None
        if self.cleaned_data.get('clear_icon'):
            instance.icon = None

        if commit:
            instance.save()

        return instance

     
      