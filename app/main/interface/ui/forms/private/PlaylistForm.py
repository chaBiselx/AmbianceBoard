import json
from django import forms
from django.utils.translation import gettext_lazy as _
from main.architecture.persistence.models.Playlist import Playlist
from main.domain.common.mixins.BootstrapFormMixin import BootstrapFormMixin
from main.domain.common.enum.ImageFormatEnum import ImageFormatEnum
from main.domain.common.enum.FadePlaylistEnum import FadePlaylistEnum
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.strategy.PlaylistStrategy import PlaylistStrategy
from main.architecture.persistence.repository.PlaylistTagRepository import PlaylistTagRepository



class PlaylistForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Playlist
        fields = (
            'name',
            'typePlaylist',
            'useSpecificColor',
            'color',
            'colorText',
            'volume',
            'icon',
            'is_copiable',
            'useSpecificDelay',
            'maxDelay',
            'fadeIn',
            'fadeOut',
            'playlist_tags',
        )
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        strategy_factory = PlaylistStrategy()
        default_fades_by_type = {
            PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name: {
                "fadeIn": strategy_factory.get_strategy(PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name).default_data['fadeInType'],
                "fadeOut": strategy_factory.get_strategy(PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name).default_data['fadeOutType'],
            },
            PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name: {
                "fadeIn": strategy_factory.get_strategy(PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name).default_data['fadeInType'],
                "fadeOut": strategy_factory.get_strategy(PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name).default_data['fadeOutType'],
            },
            PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name: {
                "fadeIn": strategy_factory.get_strategy(PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name).default_data['fadeInType'],
                "fadeOut": strategy_factory.get_strategy(PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name).default_data['fadeOutType'],
            },
        }
        self.fields['typePlaylist'].widget.attrs.update({
            'data-default-fades': json.dumps(default_fades_by_type)
        })

        # Supprime le lien si un fichier existe
        if self.instance and self.instance.icon:
            self.fields['icon'].widget.attrs.update({'placeholder': _('form.playlist.icon.choose_new_file')})
            self.fields['icon'].help_text = f"{_('form.playlist.icon.already_selected')} <a id='id_icon_alreadyexist' href='{ self.instance.icon.url }' target='_blank'>{_('form.playlist.icon.view')}</a>"
        
        
    name = forms.CharField(
        label=_('form.playlist.name.label'),
        max_length=255, 
        required=True
    )
    typePlaylist = forms.ChoiceField(
        label=_('form.playlist.type.label'),
        choices=Playlist.typePlaylist.field.choices,
        required=True,
    )
    useSpecificColor = forms.BooleanField(required=False, label=_('form.playlist.specific_color.label'), initial=False)
    color = forms.CharField(
        label=_('form.playlist.background_color.label'),
        widget=forms.TextInput(attrs={'type': 'color', 'typeInput': 'color'}),
        initial="#000000"
    )
    colorText = forms.CharField(
        label=_('form.playlist.text_color.label'),
        widget=forms.TextInput(attrs={'type': 'color', 'typeInput': 'color'}),
        initial="#ffffff"
    )
    volume = forms.IntegerField(
        label=_('form.playlist.volume.label'),
        min_value=0,
        max_value=100,
        initial=75,
        widget=forms.NumberInput(attrs={'type': 'range', 'min': 0, 'max': 100, 'typeInput': 'range'})
    )
    icon = forms.FileField(
        label=_('form.playlist.icon.label'),
        widget=forms.FileInput(attrs={'accept': ', '.join(ImageFormatEnum.values())}),
        required=False
    )
    is_copiable = forms.BooleanField(required=False, label=_('form.playlist.copiable.label'), initial=True)
    clear_icon = forms.BooleanField(required=False, label=_('form.playlist.delete_icon.label'), initial=False)
    useSpecificDelay = forms.BooleanField(required=False, label=_('form.playlist.specific_delay.label'), initial=False)
    maxDelay = forms.IntegerField(
        label=_('form.playlist.max_delay.label'),
        min_value=0,
        max_value=3600,
        initial=0
    )
    fadeIn = forms.ChoiceField(
        label=_('form.playlist.fade_in.label'),
        choices=FadePlaylistEnum.convert_to_choices(),
        initial=FadePlaylistEnum.DEFAULT.name,
        required=True
    )
    fadeOut = forms.ChoiceField(
        label=_('form.playlist.fade_out.label'),
        choices=FadePlaylistEnum.convert_to_choices(),
        initial=FadePlaylistEnum.DEFAULT.name,
        required=True
    )
    playlist_tags = forms.ModelMultipleChoiceField(
        queryset=PlaylistTagRepository().get_list_active_tags(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_('form.playlist.tags.label'),
        help_text=_('form.playlist.tags.helptext')
    )
    
    def clean_icon(self):
        if self.cleaned_data.get('clear_icon'):
            return None
        icon = self.cleaned_data['icon']
        allowed_extensions = ImageFormatEnum.values()
        if icon and not any(icon.name.lower().endswith(ext) for ext in allowed_extensions):
             raise forms.ValidationError(_('form.playlist.icon.invalid_format') % {'extensions': ', '.join(allowed_extensions)})
        return icon
    
    def save(self, commit=True):
        instance = super().save(commit=False)

        # Si le fichier doit être supprimé, on l'initialise à None
        if self.cleaned_data.get('clear_icon'):
            instance.icon = None

        if commit:
            instance.save()
            self.save_m2m()

        return instance

     
      