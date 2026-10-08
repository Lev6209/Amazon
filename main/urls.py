from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('review/', views.review, name='review'),

    path('product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),

    path('favorites/', views.favorites, name='favorites'),
    path('product/<int:product_id>/add_to_favorites/', views.add_to_favorites, name='add_to_favorites'),

    path('product/<int:product_id>/<str:product_name>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),

    # path('free/', views.free, name='free'),
    path('new/', views.new, name='new'),
    path('api/product/<int:product_id>/', views.api_product_detail, name='api_product_detail'),
    path('free_products/', views.IndexView.as_view(), {'is_free': True}, name='free_products'),
    path('paid_products/', views.IndexView.as_view(), {'is_free': False}, name='paid_products'),
    path('api/products/', views.api_products, name='api_products'),
    path('add_product/', views.AddProductView.as_view(), name='add_product'),

    path('register/', views.register, name='register'),
    path('login/', views.StoreLoginView.as_view(), name='login'),
    path('logout/', views.StoreLogoutView.as_view(), name='logout'),

    path('profile/', views.profile, name='profile'),
    path('author/<int:user_id>/', views.author_detail, name='author_detail'),

    path('password-reset/', views.StorePasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.StorePasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.StorePasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/complete/', views.StorePasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password-change/', views.StorePasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', views.StorePasswordChangeDoneView.as_view(), name='password_change_done'),




]
