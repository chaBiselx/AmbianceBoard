from typing import Any, Optional
from django import forms
from django.core.files.uploadedfile import UploadedFile
from home.models.SoundBoard import SoundBoard
from home.models.Tag import Tag
from home.mixins.BootstrapFormMixin import BootstrapFormMixin
from home.enum.ImageFormatEnum import ImageFormatEnum

class SoundBoardForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SoundBoard
        fields = ('name', 'color', 'colorText', 'is_public', 'icon', 'tags')
        
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Supprime le lien si un fichier existe
        if self.instance and self.instance.icon:
            self.fields['icon'].widget.attrs.update({'placeholder': 'Choisissez un nouveau fichier'})
            self.fields['icon'].help_text = f"Image déja choisie <a id='id_icon_alreadyexist' href='{ self.instance.icon.url }' target='_blank'>Voir</a>" 
        
        # Configuration du champ tags
        self.fields['tags'].queryset = Tag.objects.filter(is_active=True).order_by('name')
        
        # Si c'est une édition, pré-sélectionner les tags existants
        if self.instance and self.instance.pk:
            self.fields['tags'].initial = self.instance.tags.filter(is_active=True)
 
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
        widget=forms.FileInput(attrs={'accept': ', '.join(ImageFormatEnum.values())}),
        required=False
    )
    clear_icon = forms.BooleanField(required=False, label='Supprimer le fichier', initial=False)
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Tags',
        help_text='Sélectionnez si necessaires des tags pour catégoriser votre soundboard pour les recherches'
    )

    def clean_icon(self) -> Optional[UploadedFile]:
        if self.cleaned_data.get('clear_icon'):
            return None
        icon = self.cleaned_data['icon']
        allowed_extensions = ImageFormatEnum.values()
        if icon and not any(icon.name.lower().endswith(ext) for ext in allowed_extensions):
            raise forms.ValidationError(f"Seuls les fichiers images ({', '.join(allowed_extensions)}) sont autorisés.")
        return icon

    def save(self, commit: bool = True) -> SoundBoard:
        instance = super().save(commit=False)

        # Si le fichier doit être supprimé, on l'initialise à None
        if self.cleaned_data.get('clear_icon'):
            instance.icon = None

        if commit:
            instance.save()
            # Sauvegarder les relations many-to-many (tags)
            self.save_m2m()

        return instance

     