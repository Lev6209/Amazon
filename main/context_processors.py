from django.db.models import Count, Avg

from .models import Product, Category



def store_menu(request):
    categories = list(
        Category.objects
        .annotate(product_count=Count('product'))
        .order_by('name')
    )

    favorites_count = 0
    if request.user.is_authenticated:
        favorites_count = request.user.favorite_products.count()

    recently_viewed_ids = request.session.get('recently_viewed', [])

    recently_viewed = Product.objects.filter(
        id__in=recently_viewed_ids
    ).annotate(
    average_rating=Avg('review__stars')
    )

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