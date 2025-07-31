
class FileManagementException(Exception): 
    def __init__(self, message):
        super().__init__(f"FileManagementException : {message}")

class FileNoteFound(FileManagementException):
    def __init__(self, message):
        super().__init__(f"FileNoteFound : {message}")
        
class FileNotInDatabase(FileManagementException):
    def __init__(self, message):
        super().__init__(f"FileNotInDatabase : {message}")