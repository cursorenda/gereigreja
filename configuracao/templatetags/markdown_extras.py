# configuracao/templatetags/markdown_extras.py
from django import template
import markdown2

register = template.Library()

@register.filter(name='markdown')
def markdown_format(text):
    return markdown2.markdown(text)
