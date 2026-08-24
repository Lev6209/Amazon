from django.contrib import admin

from .models import Seller, Category, Product, Review

admin.site.register(Seller)
admin.site.register(Category)
admin.site.register(Product)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('username', 'product', 'stars', 'created_at')
