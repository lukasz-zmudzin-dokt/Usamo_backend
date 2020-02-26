import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User


def current_year():
    return datetime.date.today().year


def max_value_current_year(value):
    return MaxValueValidator(current_year() + 10)(value)


def validate_cv_id(cv_id):
    if not CV.objects.filter(cv_id=cv_id).exists():
        raise ValidationError('%(value)s is not a cv id',
                              params={'value': cv_id},
                              )


class CV(models.Model):
    cv_id = models.IntegerField(null=True)
    wants_verification = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)


class BasicInfo(models.Model):
    cv = models.OneToOneField(CV, related_name='basic_info', on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    picture = models.ImageField(upload_to='cv_pics/')
    phone_number = models.CharField(max_length=12)
    date_of_birth = models.CharField(max_length=12)


class School(models.Model):
    cv = models.ForeignKey(CV, related_name='schools', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    year_start = models.PositiveIntegerField(
        default=current_year(),
        validators=[
            MinValueValidator(1990),
            max_value_current_year])
    year_end = models.PositiveIntegerField(
        null=True,
        validators=[
            MinValueValidator(1990),
            max_value_current_year])
    additional_info = models.CharField(max_length=150, null=True)


class Experience(models.Model):
    cv = models.ForeignKey(CV, related_name='experiences', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=400)
    year_start = models.PositiveIntegerField(
        default=current_year(),
        validators=[
            MinValueValidator(1990),
            max_value_current_year])
    year_end = models.PositiveIntegerField(
        null=True,
        validators=[
            MinValueValidator(1990),
            max_value_current_year])


class Skill(models.Model):
    cv = models.ForeignKey(CV, related_name='skills', on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=50)


class Language(models.Model):
    cv = models.ForeignKey(CV, related_name='languages', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=20)
    level = models.CharField(max_length=20)


class Feedback(models.Model):
    cv_id = models.IntegerField(validators=[validate_cv_id])
    basic_info = models.TextField(blank=True)
    schools = models.TextField(blank=True)
    experiences = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    languages = models.TextField(blank=True)
