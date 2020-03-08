from django.contrib import admin
from .models import JobOffer

# Register your models here.

class JobOfferAdmin(admin.ModelAdmin):
    readonly_fields = ("id", )

admin.site.register(JobOffer, JobOfferAdmin)
