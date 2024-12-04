import logging
from ..models.SoundBoard import SoundBoard

class SoundBoardService:
    
    def __init__(self, request):
        self.request = request
    
    def get_soundboard(self, soundboard_id:int)-> SoundBoard|None :
        logger = logging.getLogger(__name__)
        logger.info("in static ")
        try:
            soundboard = SoundBoard.objects.get(id=soundboard_id)
            if not soundboard or soundboard.user != self.request.user:
                return None
            return soundboard
        except SoundBoard.DoesNotExist:
            return None
        

        