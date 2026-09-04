from main.domain.common.service.SoundBoardService import SoundBoardService
from main.domain.common.service.script.SoundboardScriptService import SoundboardScriptService
from main.architecture.persistence.models.SoundboardScript import SoundboardScript
from typing import Optional
from main.architecture.persistence.models.SoundBoard import SoundBoard


class ScriptResolverService:
    
    
    def __init__(self, request: "HttpRequest"):
        self.soundboard_service = SoundBoardService(request)
        
    def get_soundboard(self, soundboard_uuid) -> "SoundBoard":
        self.soundboard = self.soundboard_service.get_soundboard(soundboard_uuid)
        if not self.soundboard:
            raise ValueError("Soundboard not found")
        return self.soundboard
    
    def get_script(self, script_uuid) -> Optional["SoundboardScript"]:
        return (self.get_script_service()).get(script_uuid)
    
    def get_script_service(self) -> "SoundboardScriptService":
        return SoundboardScriptService(self.soundboard)
    
