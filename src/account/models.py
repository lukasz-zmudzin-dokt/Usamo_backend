import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.authtoken.models import Token

from .account_status import AccountStatus, ACCOUNT_STATUS_CHOICES
from .account_type import *
from .utils import create_profile_picture_file_path


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


class EmailLowerCaseField(models.EmailField):
    def get_prep_value(self, value):
        value = super(EmailLowerCaseField, self).get_prep_value(value)
        if value is not None:
            value = value.lower()
        return value


class Account(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='id')
    email = EmailLowerCaseField(verbose_name='email', max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30, verbose_name='first_name')
    last_name = models.CharField(max_length=30, verbose_name='last_name')
    date_joined = models.DateTimeField(verbose_name='date_joined', null=True)
    last_login = models.DateTimeField(verbose_name='last_login', null=True)
    profile_picture = models.ImageField(null=True, upload_to=create_profile_picture_file_path)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    status = models.IntegerField(
        default=AccountStatus.WAITING_FOR_VERIFICATION.value, choices=ACCOUNT_STATUS_CHOICES)
    type = models.IntegerField(
        default=AccountType.STANDARD.value, choices=ACCOUNT_TYPE_CHOICES)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = AccountManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    @property
    def group_type(self):
        return list(self.groups.values_list('name', flat=True))

    @property
    def picture_url(self):
        return self.profile_picture.url if self.profile_picture.name else None

    def delete_image_if_exists(self, *args, **kwargs) -> bool:
        if self.profile_picture.name:
            storage, path = self.profile_picture.storage, self.profile_picture.path
            self.profile_picture.delete()
            storage.delete(path)
            return True
        return False


class Address(models.Model):
    city = models.CharField(max_length=40)
    street = models.CharField(max_length=120)
    street_number = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=6)


class DefaultAccount(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='account')
    phone_number = PhoneNumberField()
    facility_name = models.CharField(max_length=60)
    facility_address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True)


class EmployerAccount(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='employer_account')
    phone_number = PhoneNumberField()
    company_name = models.CharField(max_length=60)
    company_address = models.OneToOneField(Address, on_delete=models.CASCADE)
    nip = models.CharField(max_length=10)


class StaffAccount(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='staff_account')
    role = models.CharField(max_length=60, null=True, blank=True)


@receiver(post_save, sender=Token)
def update_last_login(sender, instance, created, **kwargs):
    if created:
        instance.user.last_login = timezone.now()
        instance.user.save()


@receiver(post_save, sender=EmployerAccount)
def set_employer_account_type(sender, instance, created, **kwargs):
    if created:
        instance.user.type = AccountType.EMPLOYER.value


@receiver(post_save, sender=StaffAccount)
def set_admin_status(sender, instance, created, **kwargs):
    if created:
        instance.user.type = AccountType.STAFF.value
        instance.user.status = AccountStatus.VERIFIED.value
