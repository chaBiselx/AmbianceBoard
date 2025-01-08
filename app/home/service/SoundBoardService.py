from parameters import settings
from home.models.SoundBoard import SoundBoard
from home.forms.SoundBoardForm import SoundBoardForm
from home.enum.PermissionEnum import PermissionEnum
from django.contrib import messages


class SoundBoardService:
    
    def __init__(self, request):
        self.request = request
    
    def get_soundboard(self, soundboard_id:int)-> SoundBoard|None :
        try:
            soundboard = SoundBoard.objects.get(id=soundboard_id)
            if not soundboard or soundboard.user != self.request.user:
                return None
            return soundboard
        except SoundBoard.DoesNotExist:
            return None
        
    def save_form(self):
        if(self.request.user.has_perm('auth.' + PermissionEnum.USER_PREMIUM_OVER_LIMIT_SOUNDBOARD.name)):  
            limit_soundboard = settings.LIMIT_USER_PREMIUM_SOUNDBOARD
        else:
            limit_soundboard = settings.LIMIT_USER_STANDARD_SOUNDBOARD
        
        if len(SoundBoard.objects.filter(user=self.request.user)) >= limit_soundboard:
            messages.error(self.request, "Vous avez atteint la limite de soundboard (" + str(limit_soundboard) + " max).")
            return None
        
        form = SoundBoardForm(self.request.POST)
        if form.is_valid():
            soundboard = form.save(commit=False)
            soundboard.user = self.request.user
            soundboard.save()
            return soundboard
        return None
        

        