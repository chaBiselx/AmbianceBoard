from enum import Enum
from django.templatetags.static import static 

class ConfigTypeDataEnum(Enum):
    STATIC = 'Fixe'
    PARAM = 'Parametrable via playlist'
    PARAM_WITH_DEFAULT = 'Parametrable via playlist avec valeur par default'
    
    def get_icon_path(self):
        return static(f"img/ConfigType/icon_{self.name.lower()}.png")
    