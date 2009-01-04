from django import template
from django import forms 

register = template.Library()

def render_as_p(field):
    htmlclass = None
    if field.name == "honeypot":
        htmlclass="hide"
    elif isinstance(field.field.widget, forms.widgets.CheckboxInput):
        htmlclass="checkbox"
    elif isinstance(field.field.widget, forms.widgets.FileInput):
        htmlclass="file"
    elif isinstance(field.field.widget, forms.widgets.TextInput):
        htmlclass="text"
    elif isinstance(field.field.widget, forms.widgets.HiddenInput):
        htmlclass="hidden"

    return {'field': field, 'htmlclass': htmlclass}
    
register.inclusion_tag('field.html')(render_as_p)
