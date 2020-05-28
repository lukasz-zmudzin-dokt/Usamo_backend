from datetime import date
from account.serializers import AddressSerializer
from rest_framework import serializers
from .models import *


class JobOfferCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOfferCategory
        fields = ['name']


class JobOfferTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOfferType
        fields = ['name']


class JobOfferSerializer(serializers.ModelSerializer):
    voivodeship = serializers.ChoiceField(choices=Voivodeships.choices)
    company_logo = serializers.CharField(source='employer.user.picture_url', read_only=True)
    company_address = AddressSerializer()
    category = serializers.CharField(source='category.name')
    type = serializers.CharField(source='offer_type.name')

    def validate_expiration_date(self, value):
        today = date.today()
        if value < today:
            raise serializers.ValidationError("Date is in past")
        return value

    def validate(self, data):
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError("salary_min is greater than salary_max")
        return data

    def create(self, validated_data):
        validated_data['category'] = JobOfferCategory.objects.get(**validated_data['category'])
        validated_data['offer_type'] = JobOfferType.objects.get(**validated_data['offer_type'])
        company_address = Address.objects.create(**validated_data['company_address'])
        validated_data['company_address'] = company_address
        return JobOffer(**validated_data)

    def update(self, instance, validated_data):
        try:
            instance.category = JobOfferCategory.objects.get(name=validated_data.get('category', None))
        except JobOfferCategory.DoesNotExist:
            pass

        try:
            instance.offer_type = JobOfferType.objects.get(name=validated_data.get('type', None))
        except JobOfferType.DoesNotExist:
            pass

        instance.offer_name = validated_data.get('offer_name', instance.offer_name)
        instance.company_name = validated_data.get('company_name', instance.company_name)
        instance.salary_min = validated_data.get('salary_min', instance.salary_min)
        instance.salary_max = validated_data.get('salary_max', instance.salary_max)
        new_address_data = validated_data.get('company_address', None)
        if new_address_data:
            new_address = Address.objects.create(**new_address_data)
            instance.company_address.delete()
            instance.company_address = new_address
        instance.voivodeship = validated_data.get('voivodeship', instance.voivodeship)
        instance.expiration_date = validated_data.get('expiration_date', instance.expiration_date)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance


    class Meta:
        model = JobOffer
        fields = ['id', 'company_logo', 'offer_name', 'offer_image', 'category', 'type', 'salary_min', 'salary_max', 'company_name',
                  'company_address', 'voivodeship', 'expiration_date', 'description']
        read_only_fields = ['offer_image']


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
    user_id = serializers.UUIDField(source='cv.cv_user.user.id', read_only=True)
    first_name = serializers.CharField(source='cv.basic_info.first_name', read_only=True)
    last_name = serializers.CharField(source='cv.basic_info.last_name', read_only=True)
    email = serializers.CharField(source='cv.basic_info.email', read_only=True)
    phone_number = serializers.CharField(source='cv.basic_info.phone_number', read_only=True)
    date_posted = serializers.DateTimeField(read_only=True)
    was_read = serializers.BooleanField(read_only=True)

    class Meta:
        model = JobOfferApplication
        fields = ['id', 'cv', 'job_offer', 'cv_url', 'user_id', 'first_name', 'last_name', 'email','phone_number',
                'date_posted', "was_read"]
        extra_kwargs = {
            'cv': {'write_only': True}
        }

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.duplicate_docs()
        instance.save()
        return instance
