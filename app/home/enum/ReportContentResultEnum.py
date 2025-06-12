from enum import Enum
from django.templatetags.static import static 

class ReportContentResultEnum(Enum):
    INVALID = 'invalid'
    VALID = 'valid'
    SPAM = 'spam'
    DUPLICATE = 'duplicate'
    OTHER = 'other'