import uuid
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import SET_NULL
from .enums import Voivodeships
from .utils import create_job_offer_image_path
from account.models import DefaultAccount, EmployerAccount, Address
from cv.models import CV


class JobOfferCategory(models.Model):
    name = models.CharField(max_length=30, primary_key=True)


class JobOfferType(models.Model):
    name = models.CharField(max_length=30, primary_key=True)


class JobOffer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    offer_name = models.CharField(max_length=50)
    offer_image = models.ImageField(upload_to=create_job_offer_image_path, null=True)
    category = models.ForeignKey(JobOfferCategory, on_delete=SET_NULL, null=True, db_column='category')
    offer_type = models.ForeignKey(JobOfferType, on_delete=SET_NULL, null=True, db_column='offer_type')
    salary_min = models.IntegerField()
    salary_max = models.IntegerField()
    company_name = models.CharField(max_length=70)
    company_address = models.OneToOneField(Address, on_delete=models.CASCADE)
    voivodeship = models.CharField(max_length=30, choices=Voivodeships.choices)
    expiration_date = models.DateField()
    description = models.CharField(max_length=1000)
    removed = models.BooleanField(editable=False, default=False)
    confirmed = models.BooleanField(default=False)
    employer = models.ForeignKey(EmployerAccount, on_delete=models.SET_NULL, null=True, default=None)

    def __str__(self):
        return self.offer_name
        

class JobOfferApplication(models.Model):
    cv = models.ForeignKey(CV, related_name='application_cv', on_delete=models.CASCADE)
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)


class JobOfferFilters:
    def __init__(self,
                 voivodeship=None,
                 min_expiration_date=None,
                 categories=None,
                 types=None):
        self.voivodeship = voivodeship
        self.min_expiration_date = min_expiration_date
        self.categories = categories
        self.types = types

    def get_filters(self):
        filters = dict(
            voivodeship=self.voivodeship,
            expiration_date__gte=self.min_expiration_date,
            category__in=self.categories,
            offer_type__in=self.types
        )
        return {k: v for k, v in filters.items() if v is not None}
