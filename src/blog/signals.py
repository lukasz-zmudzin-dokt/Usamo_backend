from django.db.models.signals import pre_delete, pre_save, post_save
from django.dispatch import receiver
from .models import BlogPostCategory, BlogPost, BlogPostReservation
from datetime import timedelta
from django.utils import timezone

@receiver(pre_delete, sender=BlogPostCategory)
def delete_category_header(sender, instance, using, **kwargs):
    instance.delete_header_if_exists()


@receiver(pre_save, sender=BlogPostReservation)
def delete_unused_reservations(sender, instance, **kwargs):
    for res in BlogPostReservation.objects.filter(blog_post=None):
        max_diff = timedelta(minutes=300)
        if timezone.now() - res.date_created > max_diff:
            res.delete()


