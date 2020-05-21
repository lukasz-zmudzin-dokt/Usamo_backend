from django.db import models
import uuid
# Create your models here.


class PhoneContact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=120, blank=False, null=False)
    description = models.TextField()
    phone_number = models.CharField(max_length=12)