from django import template
import json
import re

register = template.Library()


@register.filter
def parse_meta_json(extra_tags):
    """
    Parse JSON from extra_tags string that contains meta:{"key": "value"}
    Returns the parsed JSON object or None if parsing fails
    """
    if not extra_tags:
        return None
    
    try:
        # Extract JSON part after "meta:"
        match = re.search(r'{.*}', extra_tags)
        if match:
            json_string = match.group(0)
            return json.loads(json_string)
    except (json.JSONDecodeError, AttributeError):
        pass
    
    return None