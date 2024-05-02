from django import template

register = template.Library()

@register.filter(name='get_key_value')
def get_key_value(dictionary, key):
    return dictionary.get(key)