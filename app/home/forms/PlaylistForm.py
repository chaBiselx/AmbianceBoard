from django import forms
from ..models.Playlist import Playlist



class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ('name', 'typePlaylist')
        
        
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
     
      