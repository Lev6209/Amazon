from django.shortcuts import render
from django.http import HttpResponse

from .models import Product


def index(request):
    products = Product.objects.all()
    return render(request, 'main/index.html', {'products': products})


def about(request):
    return render(request, 'main/about.html')

