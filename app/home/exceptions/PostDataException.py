

class PostDataException(Exception): 
    def __init__(self, message):
        super().__init__(f"PostDataException : {message}")

