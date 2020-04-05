import uuid
from django.contrib.auth.models import User
from django.db import models
from django.db.models import SET_NULL
from .enums import Voivodeships
from account.models import DefaultAccount, EmployerAccount
from cv.models import CV


class JobOfferCategory(models.Model):
    name = models.CharField(max_length=30, primary_key=True)


class JobOfferType(models.Model):
    name = models.CharField(max_length=30, primary_key=True)


class JobOffer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    offer_name = models.CharField(max_length=50)
    category = models.ForeignKey(JobOfferCategory, on_delete=SET_NULL, null=True, db_column='category')
    offer_type = models.ForeignKey(JobOfferType, on_delete=SET_NULL, null=True, db_column='offer_type')
    company_name = models.CharField(max_length=70)
    company_address = models.CharField(max_length=200)
    voivodeship = models.CharField(max_length=30, choices=Voivodeships.choices)
    expiration_date = models.DateField()
    description = models.CharField(max_length=1000)
    removed = models.BooleanField(editable=False, default=False)
    employer = models.ForeignKey(EmployerAccount, on_delete=models.SET_NULL, null=True, default=None)

    def __str__(self):
        return self.offer_name
        

class JobOfferApplication(models.Model):
    cv = models.ForeignKey(CV, related_name='application_cv', on_delete=models.CASCADE)
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)


class JobOfferEdit:
    def __init__(self,
                 offer_name=None,
                 category=None,
                 offer_type=None,
                 company_name=None,
                 company_address=None,
                 voivodeship=None,
                 expiration_date=None,
                 description=None):
        self.offer_name = offer_name
        self.category = category
        self.offer_type = offer_type
        self.company_name = company_name
        self.company_address = company_address
        self.voivodeship = voivodeship
        self.expiration_date = expiration_date
        self.description = description

    def update_dict(self):
        return {k: v for (k, v) in self.__dict__.items() if v is not None}


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
