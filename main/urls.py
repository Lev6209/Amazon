from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('review/', views.review, name='review'),
    path('product/<int:product_id>/<str:product_name>/', views.product_detail, name='product_detail'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('free/', views.free, name='free'),
    path('new/', views.new, name='new'),





]
