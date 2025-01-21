from django.core.paginator import Paginator


def extract_context_to_paginator(paginator:Paginator, page_number:int):
    if page_number < 1 :
        page_number = 1 
    if(page_number > paginator.num_pages):
        page_number = paginator.num_pages
    page_objects = paginator.get_page(page_number)
    max_page = paginator.num_pages
    min_page = 1
    step = 5
    
    page_range_group = range(max(min_page, page_number - 3), min(max_page, page_number + 3) +1 ) 
    page_range_step = range(0, max_page + 1 , step)
    
    page_range = list(set(page_range_group) | set(page_range_step))
    page_range.remove(0)
    
    
    return {
        'page_objects': page_objects,
        'paginator': {
            'page_number': str(page_number),
            'page_range' : page_range,
            'is_first_page': page_number == 1,
            'is_last_page': page_number == paginator.num_pages,
            'previous_page_number': str(page_number - 1),
            'next_page_number': str(page_number + 1),
        }
    }

