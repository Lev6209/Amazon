from django.contrib import admin

from .models import Seller, Category, Product

admin.site.register(Seller)
admin.site.register(Category)
admin.site.register(Product)

