from home.models.SoundBoard import SoundBoard
from home.models.SharedSoundboard import SharedSoundboard
from home.forms.SoundBoardForm import SoundBoardForm
from home.enum.PermissionEnum import PermissionEnum
from django.contrib import messages
from home.factory.UserParametersFactory import UserParametersFactory


class SoundBoardService:
    
    def __init__(self, request):
        self.request = request
        
    def get_all_soundboard(self)-> list[SoundBoard] :
        try:
            _query_set = SoundBoard.objects.all().order_by('updated_at')
            soundboards = _query_set.filter(user=self.request.user)
        except Exception:
            soundboards = []
        return soundboards
    
    def get_soundboard(self, soundboard_uuid:int)-> SoundBoard|None :
        try:
            soundboard = SoundBoard.objects.get(uuid=soundboard_uuid)
            if not soundboard or soundboard.user != self.request.user:
                return None
            return soundboard
        except SoundBoard.DoesNotExist:
            return None
    
    def get_public_soundboard(self, soundboard_uuid:int)-> SoundBoard|None :
        try:
            soundboard = SoundBoard.objects.get(uuid=soundboard_uuid)
            if not soundboard or not soundboard.is_public:
                return None
            return soundboard
        except SoundBoard.DoesNotExist:
            return None
        
    def get_soundboard_from_shared_soundboard(self, soundboard_uuid, token:str)-> SoundBoard|None :
        try:
            soundboard = SoundBoard.objects.get(uuid=soundboard_uuid)
            if not soundboard:
                return None
            
            shared_soundboard = SharedSoundboard.objects.get(soundboard=soundboard, token=token)
            if not shared_soundboard : 
                return None
            return soundboard

        except SoundBoard.DoesNotExist:
            return None
        except SharedSoundboard.DoesNotExist:
            return None
        
    def save_form(self):
        user_parameters = UserParametersFactory(self.request.user)
        limit_soundboard = user_parameters.limit_soundboard
        
        if len(SoundBoard.objects.filter(user=self.request.user)) >= limit_soundboard:
            messages.error(self.request, "Vous avez atteint la limite de soundboard (" + str(limit_soundboard) + " max).")
            return None
        
        form = SoundBoardForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            soundboard = form.save(commit=False)
            soundboard.user = self.request.user
            soundboard.save()
            return soundboard
        return None
        

        