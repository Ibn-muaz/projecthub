# core/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def remove_query_param(query_string, param_to_remove):
    """
    Remove a specific parameter from query string
    """
    if not query_string:
        return ''
    
    params = query_string.split('&')
    filtered_params = []
    
    for param in params:
        if not param.startswith(param_to_remove + '='):
            filtered_params.append(param)
    
    return '&'.join(filtered_params) if filtered_params else ''