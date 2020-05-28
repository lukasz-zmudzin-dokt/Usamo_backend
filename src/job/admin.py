from django.contrib import admin
from .models import JobOffer


class JobOfferAdmin(admin.ModelAdmin):
    readonly_fields = ("id", )

admin.site.register(JobOffer, JobOfferAdmin)
