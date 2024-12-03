import logging
from ..models.SoundBoard import SoundBoard

class SoundBoardService:
    
    @staticmethod
    def get_soundboard(soundboard_id:int, user_id:str)-> SoundBoard|None :
        logger = logging.getLogger(__name__)
        logger.info("in static ")
        try:
            soundboard = SoundBoard.objects.get(id=soundboard_id)
            if not soundboard or soundboard.finalUser.userID != user_id:
                return None
            return soundboard
        except SoundBoard.DoesNotExist:
            return None
        

        