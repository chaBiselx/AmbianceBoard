from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def applys_pagination(pagination):
    DOM = '<ul>'
    if pagination['is_first_page'] : 
        DOM += '<li class="disabled"><a href="#">Précédente</a></li>'
    else : 
        DOM += '<li><a href="?page='+ pagination['previous_page_number'] +'">Précédente</a></li>'
        
    for page in pagination['page_range']: 
        if page == pagination['page_number']:
            DOM += '<li class="active"><a href="?page=' + str(page) + '">' + str(page) + '</a></li>'
        else : 
            DOM += '<li ><a href="?page=' + str(page) + '">' + str(page) + '</a></li>'
            
    if pagination['is_last_page'] : 
        DOM += '<li class="disabled"><a href="#">Suivante</a></li>'
    else : 
        DOM += '<li><a href="?page='+ pagination['next_page_number'] +'">Suivante</a></li>'
  
    return mark_safe(DOM)