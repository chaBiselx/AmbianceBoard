from django import template
from main.architecture.persistence.repository.PlaylistRepository import PlaylistRepository
from main.architecture.persistence.repository.SoundBoardRepository import SoundBoardRepository



register = template.Library()
defaultjson = {"playlist": None, "user" : None, "soundboard" : None, 'contentReport' : None}

@register.inclusion_tag('partials/popupModerator.html')
def show_data_playlist(playlist):
    temp = defaultjson.copy()
    temp['playlist'] = playlist
    temp['user'] = playlist.user
    return temp
    
@register.inclusion_tag('partials/popupModerator.html')
def show_data_soundboard(soundboard):
    temp = defaultjson.copy()
    temp['soundboard'] = soundboard
    temp['user'] = soundboard.user
    return temp

@register.inclusion_tag('partials/popupModerator.html')
def show_data_user(user):
    temp = defaultjson.copy()
    temp['user'] = user
    return temp

@register.inclusion_tag('partials/popupModerator.html')
def show_data_content_report(content_report):
    temp = defaultjson.copy()
    temp['contentReport'] = content_report
    if content_report.typeElement == 'playlist':
        temp['playlist'] = PlaylistRepository().get(content_report.uuidElement)
        temp['user'] = temp['playlist'].user
    elif content_report.typeElement == 'soundboard':
        temp['soundboard'] = SoundBoardRepository().get(content_report.uuidElement)
        temp['user'] = temp['soundboard'].user
    return  temp