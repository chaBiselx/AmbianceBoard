from .BaseEnum import BaseEnum

class ErrorMessageEnum(BaseEnum): 
    METHOD_NOT_SUPPORTED = 'Méthode non supportée.'
    NOT_ACCEPTABLE = 'non accetable.'
    INTERNAL_SERVER_ERROR = 'une erreur est survenue.'
    INVALID_REQUEST_METHOD = 'Invalid request method.'
    ELEMENT_NOT_FOUND = 'Element introuvable.'