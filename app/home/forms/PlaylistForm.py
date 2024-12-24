from django import forms
from ..models.Playlist import Playlist



class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ('name', 'typePlaylist', 'color', 'colorText', 'volume')
        
        
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
    color = forms.CharField(
        label='Couleur du background',
    )
    colorText = forms.CharField(
        label='Couleur du texte',
    )
    volume = forms.IntegerField(
        label='Volume',
        min_value=0,
        max_value=100,
        initial=75,
        widget=forms.NumberInput(attrs={'type': 'range', 'min': 0, 'max': 100})
    )

     
      