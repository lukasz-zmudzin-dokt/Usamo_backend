import os

from django.db import models

# Create your models here.
from django.db.models.signals import post_delete
from django.dispatch import receiver


class PhotoLayer(models.Model):
    left = models.BooleanField(default=False)
    top = models.BooleanField(default=False)
    right = models.BooleanField(default=False)


class Tile(models.Model):
    title = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='tiles/%Y/%m/%d', null=True)
    destination = models.CharField(max_length=100)
    color = models.CharField(max_length=30)
    photo_layer = models.OneToOneField(PhotoLayer, on_delete=models.CASCADE)


@receiver(post_delete, sender=Tile)
def delete_document(sender, instance, **kwargs):
    if instance.photo:
        if os.path.isfile(instance.photo.path):
            os.remove(instance.photo.path)

