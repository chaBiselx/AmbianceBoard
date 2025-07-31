from django import template

register = template.Library()

@register.inclusion_tag('partials/pagination.html')
def applys_pagination(pagination):
    return  {'pagination': pagination}
    