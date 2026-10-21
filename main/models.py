from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.models import User
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse

from datetime import datetime

def validate_non_negative_price(value):
    if value <0:
       raise ValidationError('Цена не может быть меньше нуля')

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main:category_detail', kwargs={'category_id': self.pk})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'



class ProductQuerySet(models.QuerySet):
    def free(self):
        return self.filter(price=0)

    def paid(self):
        return self.filter(price__gt=0)

    def cheap(self):
        return self.paid().filter(price__lt=100).order_by('price')

    def newest(self):
        return self.order_by('-created_at')

    def in_category(self, category):
        return self.filter(category=category)


class ProductManager(models.Manager.from_queryset(ProductQuerySet)):
    def move_to_category(self, source, target):
        if source.pk is None or target.pk is None or source.pk == target.pk:
            raise ValueError('Нельзя перенести продукт в ту же категорию')
        with transaction.atomic():
            moved = self.model.objects.in_category(source).update(category=target)
            source.delete()
        return moved



class Seller(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Продавец'
        verbose_name_plural = 'Продавцы'

def product_icon_path(instance, filename):
    date = datetime.now()
    return f'icons/{date:%Y}/{date:%m}/{filename}'

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0, validators=[validate_non_negative_price])
    created_at = models.DateTimeField(auto_now_add=True)
    rating_avg = models.DecimalField(max_digits=2, decimal_places=1, default=0, editable=False, verbose_name="Средняя оценка")
    rating_count = models.PositiveIntegerField(default=0, editable=False,verbose_name="Количество оценок")
    seller = models.ForeignKey('Seller', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    icon = models.ImageField(upload_to=product_icon_path, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    favorited_by = models.ManyToManyField(User, related_name='favorite_products', blank=True, verbose_name='В избранном у')
    objects = ProductManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main:product_detail', kwargs={'product_id': self.pk, 'product_name': self.name})

    def price_label(self):
        if self.price == 0:
            return "Бесплатный товар"
        return f'Цена: {self.price} $'


    @classmethod
    def discounted_price(cls, percent):
        if type(percent) is not int or not 1 <= percent <= 90:
            raise ValueError('Скидка должна быть целым числом от 1 до 90 %')
        factor = (Decimal(100) - Decimal(percent)) / Decimal(100)
        discounted_products = list(cls.objects.paid())
        for product in discounted_products:
            product.price = (product.price * factor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return cls.objects.bulk_update(discounted_products, ['price'])


    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    username = models.CharField(max_length=50)
    comment = models.TextField(blank=True)
    stars = models.PositiveSmallIntegerField(
        default=5,
        validators=[
            MinValueValidator(1, message='Оценка должна быть от 1'),
            MaxValueValidator(5, message='Оценка должна быть до 5')
        ]
    )
    recommended = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Автор: {self.username}, товар: "{self.product}"'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'