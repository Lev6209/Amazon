from django.db.models import Count
from django.core.cache import cache

from .models import Product, Category



def store_menu(request):
    categories = cache.get('menu_categories')

    if categories is None:
        categories = list(
            Category.objects
            .annotate(product_count=Count('product'))
            .order_by('name')
        )
        cache.set('menu_categories', categories, 60 * 3)

    products_total = cache.get('apps_total')

    if products_total is None:
        products_total = Product.objects.count()
        cache.set('products_total', products_total, 60 * 10)

    favorites_count = 0
    if request.user.is_authenticated:
        favorites_count = request.user.favorite_products.count()

    recently_viewed_ids = request.session.get('recently_viewed', [])

    recently_viewed = Product.objects.filter(id__in=recently_viewed_ids)

    recently_viewed = sorted(
        recently_viewed,
        key=lambda product: recently_viewed_ids.index(product.id)
    )

    return {
        'categories': categories,
        'products_total': Product.objects.count(),
        'categories_total': len(categories),
        'favorites_count': favorites_count,
        'recently_viewed': recently_viewed,
    }