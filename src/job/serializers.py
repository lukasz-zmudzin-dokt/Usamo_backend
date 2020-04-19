from datetime import date

from account.models import DefaultAccount
from rest_framework import serializers

from .models import *


class JobOfferSerializer(serializers.ModelSerializer):
    voivodeship = serializers.ChoiceField(choices=Voivodeships.choices)
    category = serializers.CharField(source='category.name')
    type = serializers.CharField(source='offer_type.name')

    def validate_expiration_date(self, value):
        today = date.today()
        if value < today:
            raise serializers.ValidationError("Date is in past")
        return value

    class Meta:
        model = JobOffer
        fields = ['id', 'offer_name', 'category', 'type', 'company_name', 'company_address', 'voivodeship', 'expiration_date',
                  'description']

    def create(self, validated_data):
        validated_data['category'] = JobOfferCategory.objects.get(**validated_data['category'])
        validated_data['offer_type'] = JobOfferType.objects.get(**validated_data['offer_type'])
        return JobOffer(**validated_data)


class JobOfferEditSerializer(serializers.Serializer):
    offer_name = serializers.CharField(max_length=50, required=False)
    category = serializers.CharField(max_length=30, required=False)
    type = serializers.CharField(max_length=30, required=False)
    company_name = serializers.CharField(max_length=70, required=False)
    company_address = serializers.CharField(max_length=200, required=False)
    voivodeship = serializers.CharField(max_length=30, required=False)
    expiration_date = serializers.DateField(required=False)
    description = serializers.CharField(max_length=1000, required=False)

    def create(self, validated_data):
        if 'category' in validated_data:
            validated_data['category'] = JobOfferCategory.objects.get(name=validated_data.pop('category'))
        if 'type' in validated_data:
            validated_data['offer_type'] = JobOfferType.objects.get(name=validated_data.pop('type'))
        return JobOfferEdit(**validated_data)

    def update(self, instance, validated_data):
        if 'category' in validated_data:
            instance.category = JobOfferCategory.objects.get(name=validated_data('category'))
        if 'type' in validated_data:
            instance.offer_name = JobOfferType.objects.get(name=validated_data('type'))
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
    categories = serializers.ListField(child=serializers.CharField(max_length=30), required=False)
    types = serializers.ListField(child=serializers.CharField(max_length=30), required=False)

    def create(self, validated_data):
        return JobOfferFilters(**validated_data)

    def update(self, instance, validated_data):
        instance.voivodeship = validated_data.get('voivodeship', instance.voivodeship)
        instance.min_expiration_date = validated_data.get('min_expiration_date', instance.min_expiration_date)
        instance.categories = validated_data.get('categories', instance.categories)
        instance.types = validated_data.get('types', instance.types)
        return instance


class JobOfferApplicationSerializer(serializers.ModelSerializer):
    cv_url = serializers.UUIDField(source='cv.document.url', read_only=True)
    user_id = serializers.UUIDField(source='cv.cv_user.user.id', read_only=True)
    first_name = serializers.CharField(source='cv.cv_user.user.first_name', read_only=True)
    last_name = serializers.CharField(source='cv.cv_user.user.last_name', read_only=True)
    email = serializers.CharField(source='cv.cv_user.user.email', read_only=True)
    date_posted = serializers.DateTimeField(format='%d/%m/%Y %X', read_only=True)
    
    class Meta:
        model = JobOfferApplication
        fields = ['cv', 'job_offer', 'cv_url', 'user_id', 'first_name', 'last_name', 'email', 'date_posted']
        extra_kwargs = {
            'cv': {'write_only': True}
        }