from itertools import product
from pyclbr import Class

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse
from django.views.generic import TemplateView, ListView, DetailView, CreateView

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordChangeView,
    PasswordChangeDoneView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from django.urls import reverse, reverse_lazy

from .models import Product
from .models import Review
from .models import Category

from .forms import ReviewForm, ProductForm, RegisterForm

SORTS = {
        'price': 'price',
        '-price': '-price',
        'name': 'name',
        'new': '-created_at',
    }
# @require_GET
# def index(request, is_free=None):
#     q = request.GET.get('q', '')
#     sort = request.GET.get('sort')
#
#     if is_free is True:
#         products = Product.objects.filter(price=0)
#         title = 'Бесплатные товары:'
#
#     elif is_free is False:
#         products = Product.objects.filter(price__gt=0)
#         title = 'Платные товары:'
#
#     else:
#         products = Product.objects.all()
#         title = 'Наши продукты:'
#
#     if q:
#         products = products.filter(
#             Q(name__icontains=q) |
#             Q(description__icontains=q)
#         )
#
#         if sort is None:
#             sort = 'name'
#     else:
#         if sort is None:
#             sort = 'new'
#
#     products = products.order_by(SORTS.get(sort, '-created_at'))
#
#     daily_product = Product.objects.order_by('-price').first()
#     categories = Category.objects.all()
#
#     paginator = Paginator(products, 5)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#
#     return render(request, 'main/index.html', {
#         'q': q,
#         'sort': sort,
#         'title': title,
#         'is_free': is_free,
#         'page_obj': page_obj,
#         'products': products,
#         'daily_product': daily_product,
#         'categories': categories,
#     })

class IndexView(ListView):
    model = Product
    template_name = 'main/index.html'
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):

        q = self.request.GET.get('q', '')
        sort = self.request.GET.get('sort')
        is_free = self.kwargs.get('is_free')

        if is_free is True:
            products = Product.objects.filter(price=0)
        elif is_free is False:
            products = Product.objects.filter(price__gt=0)
        else:
            products = Product.objects.all()

        products = products.select_related('author')

        products = products.annotate(
            average_rating=Avg('review__stars')
        )


        if q:
            products = products.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            )
            if sort is None:
                sort = 'name'
        else:
            if sort is None:
                sort = 'new'

        return products.order_by(SORTS.get(sort, '-created_at'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        q = self.request.GET.get('q', '')
        sort = self.request.GET.get('sort')
        is_free = self.kwargs.get('is_free')

        just_registered = self.request.session.pop(
            'just_registered',
            False
        )

        coming_back = self.request.session.pop(
            'coming_back',
            False
        )

        if q and sort is None:
            sort = 'name'
        elif not q and sort is None:
            sort = 'new'
        if is_free is True:
            title = 'Бесплатные товары'
        elif is_free is False:
            title = 'Платные товары'
        else:
            title = 'Наши продукты'
        context['q'] = q
        context['sort'] = sort
        context['title'] = title
        context['is_free'] = is_free
        context['daily_product'] = Product.objects.order_by('-price').first()
        context['just_registered'] = just_registered
        context['coming_back'] = coming_back

        return context

# @require_GET
# def about(request):
#     return render(request, 'main/about.html')

class AboutView(TemplateView):
    template_name = 'main/about.html'


# @require_GET
# def product_detail(request, product_id, product_name):
#     product = get_object_or_404(Product, id=product_id)
#
#     if product_name != product.name:
#         return redirect('main:product_detail', product.id, product.name)
#
#     return render(request, 'main/product_detail.html', {'product': product})


class ProductDetailView(DetailView):
    model = Product
    template_name = 'main/product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'product_id'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        product_name = self.kwargs.get('product_name')
        product = self.object

        if product_name != product.name:
            return redirect(
                'main:product_detail',
                product.id,
                product.name
            )

        recently_viewed = request.session.get('recently_viewed', [])
        if product.id in recently_viewed:
            recently_viewed.remove(product.id)
        recently_viewed.insert(0, product.id)
        request.session['recently_viewed'] = recently_viewed[:7]
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = ReviewForm()
        if self.request.user.is_authenticated and 'username'in form.fields:
            form.fields.pop('username')
        context['form'] = form
        context['reviews'] = self.object.review_set.order_by('-created_at')
        context['is_favorite'] = (
                self.request.user.is_authenticated
                and self.object.favorited_by.filter(pk=self.request.user.pk).exists()
        )

        average_rating = Review.objects.filter(
            product=self.object
        ).aggregate(Avg('stars'))['stars__avg']
        context['average_rating'] = average_rating

        recently_viewed_ids = self.request.session.get('recently_viewed', [])

        recently_viewed_ids = [
            product_id
            for product_id in recently_viewed_ids
            if product_id != self.object.id
        ]

        recently_viewed = Product.objects.filter(
            id__in=recently_viewed_ids
        ).annotate(
            average_rating=Avg('review__stars')
        )

        recently_viewed = sorted(
            recently_viewed,
            key=lambda product: recently_viewed_ids.index(product.id)
        )
        context['recently_viewed'] = recently_viewed

        return context


@require_POST
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    data = request.POST.copy()
    if request.user.is_authenticated:
        data['username'] = request.user.username
    form = ReviewForm(data)

    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.save()
        messages.success(request, 'Спасибо, ваш отзыв добавлен!')
        return redirect('main:product_detail', product.id, product.name)

    if request.user.is_authenticated and 'username' in form.fields:
        form.fields.pop('username')
    reviews = product.review_set.order_by('-created_at')

    return render(request, 'main/product_detail.html', {
        'product': product,
        'form': form,
        'reviews': reviews,
        'is_favorite': request.user.is_authenticated and product.favorited_by.filter(pk=request.user.pk).exists()
    })


@require_GET
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


@require_GET
def review(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'main/review.html', {'reviews': reviews})

# @require_GET
# def free(request):
#     products = Product.objects.filter(price=0)
#     return render(request, 'main/free.html', {'products': products})

@require_GET
def new(request):
    products = Product.objects.order_by('-created_at')

    paginator = Paginator(products, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'main/new.html', {
        'products': products,
        'page_obj': page_obj
    })

@require_GET
def api_product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price
    }
    return JsonResponse(data)

@require_GET
def api_products(request):
    products = Product.objects.all()
    data = []
    for product in products:
        data.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'rating': product.rating
        })
    return JsonResponse(data, safe=False)

# @login_required
# def add_product(request):
#     if request.method == 'POST':
#         form = ProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             product = form.save()
#             messages.success(request,'Товар успешно добавлен!')
#
#             return redirect('main: product_detail', product_id=product.id, product_name=product.name)
#     else:
#         form = ProductForm()
#     return render(request, 'main/add_product.html', {'form': form})

class AddProductView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'main/add_product.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request,'Товар успешно добавлен!')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('main:product_detail',kwargs={
            'product_id': self.object.id,
            'product_name': self.object.name,
        }
        )

def register(request):
    if request.user.is_authenticated:
        return redirect('main:index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session['just_registered'] = True
            return redirect('main:index')
    else:
        form = RegisterForm()
    return render(request, 'main/register.html', {'form': form})


class StoreLoginView(LoginView):
    template_name = 'main/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session['coming_back'] = True
        return response

class StoreLogoutView(LogoutView):
    next_page = reverse_lazy('main:index')


@login_required
def profile(request):
    reviews = Review.objects.filter(username=request.user.username).order_by('-created_at')

    products = Product.objects.filter(author=request.user).annotate(average_rating=Avg('review__stars')).order_by('-created_at')

    return render(request, 'main/profile.html', {
        'reviews': reviews,
        'products': products
    })

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if not (
            request.user.has_perm('main.change_product')
            or request.user.is_staff
            or product.author_id == request.user.id
    ):
        messages.error(request, 'Редактировать карту продукта может только автор')
        return redirect('main:product_detail', product_id=product.id, product_name=product.name)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Карта товара {product.name} обновлена успешно!")
            return redirect('main:product_detail', product_id=product.id, product_name=product.name)
    else:
        form = ProductForm(instance=product)
    return render(request, 'main/edit_product.html', {
        'form': form,
        'product': product
    })

@login_required
@require_POST
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.author_id != request.user.id:
        messages.error(request, 'Удалять товар может только его автор')
        return redirect('main:product_detail', product_id=product.id, product_name=product.name)

    product.delete()
    messages.success(request, 'Товар удален успешно!')
    return redirect('main:index')

def author_detail(request, user_id):
    author = get_object_or_404(User, id=user_id)
    products = Product.objects.filter(author=author).order_by('-created_at')

    return render(request, 'main/author_detail.html', {
        'author': author,
        'products': products
    })

class StorePasswordResetView(PasswordResetView):
    template_name = 'main/password_reset_form.html'
    email_template_name = 'main/password_reset_email.html'
    subject_template_name = 'main/password_reset_subject.txt'
    success_url = reverse_lazy('main:password_reset_done')

    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        form.fields['email'].label = 'Электронная почта'
        return form


class StorePasswordResetDoneView(PasswordResetDoneView):
    template_name = 'main/password_reset_done.html'

class StorePasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'main/password_reset_confirm.html'
    success_url = reverse_lazy('main:password_reset_complete')

    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        if form is not None and 'new_password1' in form.fields:
            form.fields['new_password1'].label = 'Новый пароль'
            form.fields['new_password2'].label = 'Повтор пароля'
        return form

class StorePasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'main/password_reset_complete.html'


class StorePasswordChangeView(PasswordChangeView):
    template_name = 'main/password_change_form.html'
    success_url = reverse_lazy('main:password_change_done')

class StorePasswordChangeDoneView(TemplateView):
    template_name = 'main/password_change_done.html'

@login_required()
def favorites(request):
    products = request.user.favorite_products.select_related('category', 'author').order_by('name')
    return render(request, 'main/favorites.html', {'products': products})

@require_POST
def add_to_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not request.user.is_authenticated:
        login_url = reverse('main:login')
        next_url = reverse(
            'main:product_detail',
            args=[product.id, product.name]
        )
        return redirect(f'{login_url}?next={next_url}')

    if product.favorited_by.filter(pk=request.user.pk).exists():
        product.favorited_by.remove(request.user)
        messages.success(
            request,
            f'Товар "{product.name}" удален из избранных'
        )
    else:
        product.favorited_by.add(request.user)
        messages.success(
            request,
            f'Товар "{product.name}" добавлен в избранные'
        )

    next_url = request.POST.get('next')

    if next_url:
        return redirect(next_url)

    return redirect(
        'main:product_detail',
        product_id=product.id,
        product_name=product.name
    )