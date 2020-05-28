import os
from django.db import models
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

    @property
    def photo_url(self):
        return self.photo.url if self.photo else None 


@receiver(post_delete, sender=Tile)
def delete_photo(sender, instance, **kwargs):
    if instance.photo:
        if os.path.isfile(instance.photo.path):
            os.remove(instance.photo.path)


def delete_previous_photo(instance):
    if instance.photo:
        if os.path.isfile(instance.photo.path):
            os.remove(instance.photo.path)