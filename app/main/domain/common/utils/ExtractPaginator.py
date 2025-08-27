from django.core.paginator import Paginator


def extract_context_to_paginator(paginator:Paginator, page_number:int):
    max_page = paginator.num_pages # +1 to include the last page in the range
    # Ensure page_number is within valid range
    if page_number < 1 :
        page_number = 1 
    if(page_number > max_page):
        page_number = max_page
        
    page_objects = paginator.get_page(page_number)
    min_page = 1
    step = 5
    proximity_page = 3

    page_range_group = range(max(min_page, page_number - proximity_page), min(max_page, page_number + proximity_page) + 1)
    page_range_step = range(step, max_page + 1, step)

    page_range = list(set(page_range_group) | set(page_range_step))

    
    
    return {
        'page_objects': page_objects,
        'paginator': {
            'page_number': page_number,
            'page_range' : page_range,
            'is_first_page': page_number == 1,
            'is_last_page': page_number == max_page,
            'previous_page_number': str(page_number - 1),
            'next_page_number': str(page_number + 1),
        }
    }

