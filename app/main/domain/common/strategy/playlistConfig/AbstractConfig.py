from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.enum.FadeEnum import FadeEnum
from main.domain.common.enum.ConfigTypeDataEnum import ConfigTypeDataEnum
from main.domain.common.exceptions.ConfigPlaylistTypeException import ConfigPlaylistTypeException

class AbstractConfig():
    structure_data = {
            "id": ConfigTypeDataEnum.PARAM, 
            "type": ConfigTypeDataEnum.STATIC, 
            "fadeIn": ConfigTypeDataEnum.STATIC, 
            "fadeInDuration": ConfigTypeDataEnum.STATIC,
            "fadeInType": ConfigTypeDataEnum.STATIC,
            "fadeOut": ConfigTypeDataEnum.STATIC, 
            "fadeOutDuration": ConfigTypeDataEnum.STATIC,
            "fadeOutType": ConfigTypeDataEnum.STATIC,
            "loop": ConfigTypeDataEnum.STATIC,
            "singleConcurrentRead":ConfigTypeDataEnum.STATIC,
            "volume" : ConfigTypeDataEnum.PARAM_WITH_DEFAULT,
            "delay" : ConfigTypeDataEnum.PARAM_WITH_DEFAULT
        }
    default_data = {}
    
    def get_data(self, playlist):
        specifique_data = self.default_data
        specifique_data['id'] = playlist.uuid
        if(specifique_data['volume'] is not None and playlist.volume >= 0 and playlist.volume <= 100):
            specifique_data['volume'] = playlist.volume
        if(playlist.useSpecificDelay and playlist.maxDelay >= 0):
            specifique_data['delay'] = playlist.maxDelay
        return specifique_data
    

    
    def get_structure(self):
        structure = {}
        for key in self.structure_data.keys():
            obj = {
                "condition": self.structure_data[key],
                "value" : None,
                "default" : None
            }
            if(self.structure_data[key] == ConfigTypeDataEnum.STATIC):
                obj["default"] = self.default_data[key]
                obj["value"] = self.default_data[key]
            elif(self.structure_data[key] == ConfigTypeDataEnum.PARAM):
                obj["default"] = None
                obj["value"] = None
            elif(self.structure_data[key] == ConfigTypeDataEnum.PARAM_WITH_DEFAULT):
                obj["default"] = self.default_data[key]
            else:
                raise ConfigPlaylistTypeException("wrong key in structure")
            structure[key] = obj
        return structure
    
    
    