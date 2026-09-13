from django.urls import path


from . import views
from .views import api_products

app_name = 'main'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('review/', views.review, name='review'),
    path('product/<int:product_id>/<str:product_name>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),

    # path('free/', views.free, name='free'),
    path('new/', views.new, name='new'),
    path('api/product/<int:product_id>/', views.api_product_detail, name='api_product_detail'),
    path('free_products/', views.IndexView.as_view(), {'is_free': True}, name='free_products'),
    path('paid_products/', views.IndexView.as_view(), {'is_free': False}, name='paid_products'),
    path('api/products/', views.api_products, name='api_products')
]
