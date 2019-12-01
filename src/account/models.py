from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from .account_status import AccountStatus, ACCOUNT_STATUS_CHOICES


# Create your models here.

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = PhoneNumberField()
    status = models.IntegerField(default=AccountStatus.WAITING_FOR_VERIFICATION.value, choices=ACCOUNT_STATUS_CHOICES)


@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)
        Account.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_account(sender, instance, **kwargs):
    instance.account.save()

