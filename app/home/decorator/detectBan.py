from typing import Callable, Any
import functools
from django.http import HttpRequest, HttpResponse
from home.models.SoundBoard import SoundBoard
from django.shortcuts import render
from home.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum

def detect_ban(func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> HttpResponse:
        if kwargs['soundboard_uuid'] is not None:
            soundboard = SoundBoard.objects.get(uuid=kwargs['soundboard_uuid'])
            if soundboard.user.checkBanned(): 
                return render(args[0], HtmlDefaultPageEnum.ERROR_404.value, status=404)
        return func(*args, **kwargs)
    return wrapper