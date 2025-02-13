import functools
from home.models.SoundBoard import SoundBoard
from django.shortcuts import render

def detect_ban(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs['soundboard_id'] is not None:
            soundboard = SoundBoard.objects.get(id=kwargs['soundboard_id'])
            if soundboard.user.checkBanned(): 
                return render(args[0], 'Html/General/404.html', status=404)
        return func(*args, **kwargs)
    return wrapper