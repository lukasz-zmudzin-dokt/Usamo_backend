from django.db import models
import uuid
# Create your models here.


class PhoneContact(models.Model):
    title = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=12)