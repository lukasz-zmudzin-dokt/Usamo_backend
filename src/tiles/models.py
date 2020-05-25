from django.db import models

# Create your models here.


class PhotoLayer(models.Model):
    photo_layer_left = models.BooleanField(default=False)
    photo_layer_top = models.BooleanField(default=False)
    photo_layer_right = models.BooleanField(default=False)


class Tile(models.Model):
    title = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='tiles/%Y/%m/%d', null=True)
    destination = models.CharField(max_length=100)
    color = models.CharField(max_length=30)
    photo_layer = models.OneToOneField(PhotoLayer, on_delete=models.CASCADE)
