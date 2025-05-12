from django import template

register = template.Library()

@register.filter
def get_field(form, field_name):
    """
    Récupère un champ spécifique d'un formulaire par son nom.
    """
    return form[field_name] 