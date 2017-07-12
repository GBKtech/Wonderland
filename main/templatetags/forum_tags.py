from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
import re
register = template.Library()

@register.filter(needs_autoescape=True)
@stringfilter
def mention(value, arg, autoescape=True):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    
    result = '<mark>%s</mark>' % (esc(arg))
    pattern = re.compile(re.escape(arg), re.IGNORECASE)
    return mark_safe(pattern.sub(result, value))

