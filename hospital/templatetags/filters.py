from django import template
from datetime import date

register = template.Library()


@register.filter
def calculate_age(birth_date):
    if not birth_date:
        return 0
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age
