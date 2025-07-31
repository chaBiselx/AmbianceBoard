
class EmailException(Exception): 
    def __init__(self, message):
        super().__init__(f"Email Exception : {message}")

class DebugModeActivedWitoutDebugMailException(EmailException):
    def __init__(self, message):
        super().__init__(f"Debug actived witout debug mail {message}")
        
class AttachementException(EmailException):
    def __init__(self, message):
        super().__init__(f"Error with attachement : {message}")
    
class SendException(EmailException):
    def __init__(self, message):
        super().__init__(f"Error to send : {message}")