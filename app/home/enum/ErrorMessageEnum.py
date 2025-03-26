from enum import Enum

class ErrorMessageEnum(Enum): 
    METHOD_NOT_SUPPORTED = 'Méthode non supportée.'
    NOT_ACCEPTABLE = 'non accetable.'
    INTERNAL_SERVER_ERROR = 'une erreur est survenue.'
    INVALID_REQUEST_METHOD = 'Invalid request method.'