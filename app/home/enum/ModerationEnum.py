from enum import Enum, auto

class ModerationEnum(Enum):
    """
    Énumération des tags de modération possibles
    """
    LANGUAGE = "language"
    HARASSMENT = "harassment"
    INAPPROPRIATE_CONTENT = "inappropriate content"
    SPAM = "spam"
    COPYRIGHT = "copyright"
    OTHER = "other"