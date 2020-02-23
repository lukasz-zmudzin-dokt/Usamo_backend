from rest_framework import serializers
from django.contrib.auth.models import User
from phonenumber_field.validators import validate_international_phonenumber
from django.core.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField

from .models import *


class JobOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOffer
        fields = ['offer_name', 'company_name', 'company_address', 'voivodeship', 'expiration_date',
                  'description']


class JobOfferEditSerializer(serializers.Serializer):
    offer_id = serializers.IntegerField(required=True)
    offer_name = serializers.CharField(max_length=50, required=False)
    company_name = serializers.CharField(max_length=70, required=False)
    company_address = serializers.CharField(max_length=200, required=False)
    voivodeship = serializers.CharField(max_length=30, required=False)
    expiration_date = serializers.DateField(required=False)
    description = serializers.CharField(max_length=1000, required=False)

    def create(self, validated_data):
        return JobOfferEdit(**validated_data)

    def update(self, instance, validated_data):
        instance.offer_name = validated_data.get('offer_name', instance.offer_name)
        instance.company_name = validated_data.get('company_name', instance.company_name)
        instance.company_address = validated_data.get('company_address', instance.company_address)
        instance.voivodeship = validated_data.get('voivodeship', instance.voivodeship)
        instance.expiration_date = validated_data.get('expiration_date', instance.expiration_date)
        instance.description = validated_data.get('description', instance.description)
        return instance


class JobOfferFiltersSerializer(serializers.Serializer):
    voivodeship = serializers.CharField(max_length=30, required=False)
    min_expiration_date = serializers.DateField(required=False)

    def create(self, validated_data):
        return JobOfferFilters(**validated_data)

    def update(self, instance, validated_data):
        instance.voivodeship = validated_data.get('voivodeship', instance.voivodeship)
        instance.min_expiration_date = validated_data.get('min_expiration_date', instance.min_expiration_date)
        return instance
