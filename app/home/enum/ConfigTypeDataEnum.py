from enum import Enum
from django.templatetags.static import static 

class ConfigTypeDataEnum(Enum):
    STATIC = 'Fixe'
    PARAM = 'Parametrable via playlist'
    PARAM_WITH_DEFAULT = 'Parametrable via playlist avec valeur par default'
    
    def get_icon_path(self):
        return static(f"img/ConfigType/icon_{self.name.lower()}.png")
    
    def get_icon_class(self):
        default_class ={
            self.STATIC.name: "fa-solid fa-lock",
            self.PARAM.name: "fa-solid fa-i-cursor",
            self.PARAM_WITH_DEFAULT.name: "fa-solid fa-pen"
        }
        return default_class.get(self.name, "fa-solid fa-lock")