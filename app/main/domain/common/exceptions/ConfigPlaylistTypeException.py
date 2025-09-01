
class ConfigPlaylistTypeException(Exception): 
    def __init__(self, message):
        super().__init__(f"ConfigPlaylistType : {message}")

