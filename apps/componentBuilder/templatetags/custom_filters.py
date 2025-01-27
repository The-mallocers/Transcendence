from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    try :
        return dictionary[key] 
    except :
        return -1
    
    