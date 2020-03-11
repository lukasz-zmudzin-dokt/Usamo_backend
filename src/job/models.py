from django.contrib.auth.models import User
from django.db import models

from .enums import Voivodeships
from account.models import DefaultAccount, EmployerAccount


class JobOffer(models.Model):
    offer_name = models.CharField(max_length=50)
    company_name = models.CharField(max_length=70)
    company_address = models.CharField(max_length=200)
    voivodeship = models.CharField(max_length=30, choices=Voivodeships.choices)
    expiration_date = models.DateField()
    description = models.CharField(max_length=1000)
    removed = models.BooleanField(editable=False, default=False)
    interested_users = models.ManyToManyField(DefaultAccount)
    employer = models.ForeignKey(EmployerAccount, on_delete=models.SET_NULL, null=True, default=None)

    def __str__(self):
        return self.offer_name


class JobOfferEdit:
    def __init__(self,
                 offer_name=None,
                 company_name=None,
                 company_address=None,
                 voivodeship=None,
                 expiration_date=None,
                 description=None):
        self.offer_name = offer_name
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
                 min_expiration_date=None):
        self.voivodeship = voivodeship
        self.min_expiration_date = min_expiration_date

    def get_filters(self):
        filters = dict(
            voivodeship=self.voivodeship,
            expiration_date__gte=self.min_expiration_date
        )
        return {k: v for k, v in filters.items() if v is not None}
