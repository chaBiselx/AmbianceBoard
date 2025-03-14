import os 
import re

class StaticFilesService:
    folder = None

    def __init__(self, folder:str):
        self.folder = folder
        
    
    def search(self, filename: str) -> str|None:
        files = os.listdir(self.folder)
        print(files)
    
        js_files = [f for f in files if re.match(rf"{filename}\.[a-zA-Z0-9-_]+\.js", f)]
        return js_files[0] if js_files else None
        