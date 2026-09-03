from django.shortcuts import render, get_object_or_404

from .models import Product
from .models import Review
from .models import Category


def index(request):
    products = Product.objects.all()
    daily_product = Product.objects.order_by('-price').first()
    categories = Category.objects.all()
    return render(request, 'main/index.html', {
        'products': products,
        'daily_product': daily_product,
        'categories': categories,
    })

def about(request):
    return render(request, 'main/about.html')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'main/product_detail.html', {'product': product})


def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    expensive = Product.objects.filter(price__isnull=False, price__gt=0,category=category).order_by('-price').first()
    return render(request, 'main/category.html', {'category': category, 'products': products, 'expensive': expensive})


def review(request):
    reviews = Review.objects.all()
    return render(request, 'main/review.html', {'reviews': reviews})

