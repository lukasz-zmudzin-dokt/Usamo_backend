from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import BlogPostCategory


@receiver(pre_delete, sender=BlogPostCategory)
def delete_category_header(sender, instance, using, **kwargs):
    instance.delete_header_if_exists()
