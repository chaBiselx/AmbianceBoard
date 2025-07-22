from home.models.LinkMusic import LinkMusic
from home.forms.LinkMusicForm import LinkMusicForm


class LinkService:
    
    def __init__(self, request):
        self.request = request
    
    def get_link(self, link_id: int) -> LinkMusic | None:
        """Récupère un lien musical par son ID"""
        try:
            return LinkMusic.objects.get(id=link_id)
        except LinkMusic.DoesNotExist:
            return None
    
    def save_form(self, playlist, link: LinkMusic = None) -> LinkMusic:
        """Sauvegarde un formulaire de lien musical"""
        form = LinkMusicForm(self.request.POST, instance=link)
        
        if form.is_valid():
            link_music = form.save(commit=False)
            link_music.playlist = playlist
            link_music.save()
            return link_music
        else:
            # Lever une exception avec les erreurs du formulaire
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            raise ValueError("; ".join(error_messages))
