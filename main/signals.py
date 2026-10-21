from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Avg, Count
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail

from .models import Product, Review

def refresh_product_rating(product_id):
    stats = Review.objects.filter(product_id=product_id).aggregate(
        avg=Avg('stars'),
        total=Count('id')
    )
    total = stats['total'] or 0

    if stats['avg'] is None:
        rating = Decimal('0.0')
    else:
        rating = Decimal(str(stats['avg'])).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    Product.objects.filter(pk=product_id).update(
        rating_avg=rating,
        rating_count=total
    )



@receiver(post_save, sender=Review, dispatch_uid='main.review_saved_refresh_rating')
def review_saved(sender, instance, created, **kwargs):
    refresh_product_rating(instance.product_id)

    if created:
        product = instance.product
        author = product.author

        if author and author.email:
            def send_review_email():
                send_mail(
                    subject=f'Новый отзыв на товар «{product.name}»',
                    message=(
                        f'На ваш товар «{product.name}» оставлен новый отзыв.\n\n'
                        f'Автор отзыва: {instance.username}\n'
                        f'Оценка: {instance.stars} из 5\n\n'
                        f'Комментарий:\n{instance.comment}'
                    ),
                    from_email=None,
                    recipient_list=[author.email],
                    fail_silently=True,
                )

            transaction.on_commit(send_review_email)


@receiver(post_delete, sender=Review, dispatch_uid='main.review_deleted_refresh_rating')
def review_deleted(sender, instance, **kwargs):
    refresh_product_rating(instance.product_id)