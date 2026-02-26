from django import template

register = template.Library()

@register.filter
def stringformat_d(value):
    """Преобразование числа в строку для сравнения в шаблоне"""
    return str(value)
