from ..models.SoundBoard import SoundBoard

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
        

        