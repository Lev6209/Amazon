from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Product
from .models import Review
from .models import Category

SORTS = {
        'price': 'price',
        '-price': '-price',
        'name': 'name',
        'new': '-created_at',
    }
def index(request):
    q = request.GET.get('q', '')
    sort = request.GET.get('sort')

    if q:
        products = Product.objects.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )

        if sort is None:
            sort = 'name'

    else:
        products = Product.objects.all()

        if sort is None:
            sort = 'new'

    products = products.order_by(SORTS.get(sort, '-created_at'))
    daily_product = Product.objects.order_by('-price').first()
    categories = Category.objects.all()

    paginator = Paginator(products, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'main/index.html', {
        'q': q,
        'page_obj': page_obj,
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
    q = request.GET.get('q', '')
    products = Product.objects.filter(category=category)

    if q:
        products = products.filter(Q(name__icontains=q)|Q(description__icontains=q))

    sort = request.GET.get('sort')
    if sort == 'price':
        products = products.order_by('price')
    elif sort == '-price':
        products = products.order_by('-price')

    expensive = Product.objects.filter(price__isnull=False, price__gt=0,category=category).order_by('-price').first()

    paginator = Paginator(products, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'main/category.html', {
        'q':q,
        'page_obj': page_obj,
        'category': category,
        'products': products,
        'expensive': expensive
    })


def review(request):
    reviews = Review.objects.all()
    return render(request, 'main/review.html', {'reviews': reviews})

def free(request):
    products = Product.objects.filter(price=0)
    return render(request, 'main/free.html', {'products': products})

def new(request):
    products = Product.objects.order_by('-created_at')

    paginator = Paginator(products, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'main/new.html', {
        'products': products,
        'page_obj': page_obj
    })
