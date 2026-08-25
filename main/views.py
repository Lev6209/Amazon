from django.shortcuts import render
from django.http import HttpResponse

from .models import Product
from .models import Review


def index(request):
    products = Product.objects.all()
    daily_product = Product.objects.order_by('-price').first()
    return render(request, 'main/index.html', {
        'products': products,
        'daily_product': daily_product
    })


def about(request):
    return render(request, 'main/about.html')


def review(request):
    reviews = Review.objects.all()
    return render(request, 'main/review.html', {'reviews': reviews})

