from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.authtoken.models import Token

from .account_status import AccountStatus, ACCOUNT_STATUS_CHOICES


class AccountManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password=None):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have a username')
        if not first_name:
            raise ValueError('User must have a first name')
        if not last_name:
            raise ValueError('User must have a last name')
        user = self.model(email=self.normalize_email(email), username=username, first_name=first_name,
                          last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name, password):
        user = self.create_user(email=self.normalize_email(email), username=username, first_name=first_name,
                                last_name=last_name)
        user.set_password(password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30, verbose_name='first_name')
    last_name = models.CharField(max_length=30, verbose_name='last_name')
    date_joined = models.DateTimeField(verbose_name='date_joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last_login', auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    status = models.IntegerField(default=AccountStatus.WAITING_FOR_VERIFICATION.value, choices=ACCOUNT_STATUS_CHOICES)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = AccountManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class DefaultAccount(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    phone_number = PhoneNumberField()
    facility_name = models.CharField(max_length=60)
    facility_address = models.CharField(max_length=120)


class EmployerAccount(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='employer_account')
    phone_number = PhoneNumberField()
    company_name = models.CharField(max_length=60)
    company_address = models.CharField(max_length=120)
    nip = models.CharField(max_length=10)


@receiver(post_save, sender=Account)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)
