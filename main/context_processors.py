from django.db.models import Count

from .models import Product, Category

def store_menu(request):
    categories = list(
        Category.objects
        .annotate(product_count=Count('product'))
        .order_by('name')
    )
    return {
        'categories': categories,
        'products_total': Product.objects.count(),
        'categories_total': len(categories),
    }