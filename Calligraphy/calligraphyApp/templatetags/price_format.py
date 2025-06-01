from django import template
import re

register = template.Library()

@register.filter
def format_price(value):
    """
    Format a price by removing decimal part (.00) and adding slashes for thousands separator
    Example: 1580000.00 -> 1/580/000
    """
    if not value:
        return "0"
    
    # Convert to string and remove any decimal part
    str_value = str(value)
    str_value = str_value.split('.')[0]
    
    # Get the length of the string
    length = len(str_value)
    
    # Format with slashes
    if length > 6:  # For prices in millions (e.g., 1,580,000)
        return f"{str_value[:-6]}/{str_value[-6:-3]}/{str_value[-3:]}"
    elif length > 3:  # For prices in thousands (e.g., 980,000)
        return f"{str_value[:-3]}/{str_value[-3:]}"
    else:
        return str_value 