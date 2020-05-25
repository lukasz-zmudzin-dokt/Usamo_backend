from django.db import models

# Create your models here.


class Tile(models.Model):
    title = models.CharField(max_length=100)
    photo = models.URLField(null=True)
    destination = models.CharField(max_length=100)
    color = models.CharField(max_length=30)
    photo_layer_left = models.BooleanField(default=False)
    photo_layer_top = models.BooleanField(default=False)
    photo_layer_right = models.BooleanField(default=False)