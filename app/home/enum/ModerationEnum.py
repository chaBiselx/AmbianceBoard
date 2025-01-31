from enum import Enum, auto

class ModerationEnum(Enum):
    """
    Énumération des tags de modération possibles
    """
    LANGUAGE = auto()
    HARASSMENT = auto()
    INAPPROPRIATE_CONTENT = auto()
    SPAM = auto()
    COPYRIGHT = auto()
    OTHER = auto()