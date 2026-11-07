from django import template
register = template.Library()

@register.filter
def hearts(value):
    full = int(value)
    return '🩷' * full + '🩶' * (5 - full)

@register.filter
def reviews_count(value):
    value = int(value)

    if 11 <= value % 100 <= 14:
        word = 'отзывов'
    elif value % 10 == 1:
        word = 'отзыв'
    elif 2 <= value % 10 <= 4:
        word = 'отзыва'
    else:
        word = 'отзывов'

    return f'{value} {word}'

@register.filter
def categories_count(value):
    value = int(value)

    if 11 <= value % 100 <= 14:
        word = 'категорий'
    elif value % 10 == 1:
        word = 'категория'
    elif 2 <= value % 10 <= 4:
        word = 'категории'
    else:
        word = 'категорий'

    return f'{value} {word}'

@register.filter
def products_count(value):
    value = int(value)

    if 11 <= value % 100 <= 14:
        word = 'товаров'
    elif value % 10 == 1:
        word = 'товар'
    elif 2 <= value % 10 <= 4:
        word = 'товара'
    else:
        word = 'товаров'

    return f'{value} {word}'

@register.filter
def sale_count(value):
    value = int(value)

    if 11 <= value % 100 <= 14:
        word = 'товарам'
    elif value % 10 == 1:
        word = 'товару'
    elif 2 <= value % 10 <= 4:
        word = 'товарам'
    else:
        word = 'товарам'

    return f'{value} {word}'

@register.filter
def end_sale_count(value):
    value = int(value)

    if 11 <= value % 100 <= 14:
        word = 'товаров'
    elif value % 10 == 1:
        word = 'товара'
    elif 2 <= value % 10 <= 4:
        word = 'товаров'
    else:
        word = 'товаров'

    return f'{value} {word}'


@register.filter
def my_prices(value):
    value = int(value)

    if 11 <= value % 100 <= 14:
        word = 'карт товаров'
    elif value % 10 == 1:
        word = 'карта товара'
    elif 2 <= value % 10 <= 4:
        word = 'карты товаров'
    else:
        word = 'карт товаров'

    return f'{value} {word}'