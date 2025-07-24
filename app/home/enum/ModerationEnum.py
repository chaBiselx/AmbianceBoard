from .BaseEnum import BaseEnum

class ModerationEnum(BaseEnum):
    """
    Énumération des tags de modération possibles
    """
    LANGUAGE = "language"
    HARASSMENT = "harassment"
    INAPPROPRIATE_CONTENT = "inappropriate content"
    SPAM = "spam"
    COPYRIGHT = "copyright"
    OTHER = "other"