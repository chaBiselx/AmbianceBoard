from django import forms
from home.models.SoundBoard import SoundBoard
from home.mixins.BootstrapFormMixin import BootstrapFormMixin

class SoundBoardForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SoundBoard
        fields = ('name', 'color', 'colorText', 'is_public', 'icon')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Supprime le lien si un fichier existe
        if self.instance and self.instance.icon:
            self.fields['icon'].widget.attrs.update({'placeholder': 'Choisissez un nouveau fichier'})
            self.fields['icon'].help_text = f"Image déja choisie <a id='id_icon_alreadyexist' href='{ self.instance.icon.url }' target='_blank'>Voir</a>" 
 
    name = forms.CharField(
        label='Nom du soundboard', 
        widget=forms.TextInput(attrs={'typeInput': 'text'}),
        max_length=64, 
        required=True
    )
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
    is_public = forms.BooleanField(
        required=False, 
        label='Partager le soundboard', 
        initial=False
    )
    icon = forms.FileField(
        label='Icone de la playlist', 
        widget=forms.FileInput(attrs={'accept': '.jpg, .jpeg, .jfif, .pjpeg, .pjp, .png, .svg, .webp'}),
        required=False
    )
    clear_icon = forms.BooleanField(required=False, label='Supprimer le fichier', initial=False)

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

     