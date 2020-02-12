from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from .account_status import AccountStatus, ACCOUNT_STATUS_CHOICES


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = PhoneNumberField()
    facility_name = models.CharField(max_length=60)
    facility_address = models.CharField(max_length=120)
    status = models.IntegerField(default=AccountStatus.WAITING_FOR_VERIFICATION.value, choices=ACCOUNT_STATUS_CHOICES)


class EmployerAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_account')
    phone_number = PhoneNumberField()
    company_name = models.CharField(max_length=60)
    company_address = models.CharField(max_length=120)
    nip = models.CharField(max_length=10)
    status = models.IntegerField(default=AccountStatus.WAITING_FOR_VERIFICATION.value, choices=ACCOUNT_STATUS_CHOICES)


@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)
