from rest_framework import serializers
from django.contrib.auth.models import User
from phonenumber_field.validators import validate_international_phonenumber
from django.core.exceptions import ValidationError
from .models import *


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['name', 'year_start', 'year_end']


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['title', 'description', 'year_start', 'year_end']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['description']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['name', 'level']


class CVSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='cv.phone_number')
    schools = SchoolSerializer(many=True)
    experiences = ExperienceSerializer(many=True)
    skills = SkillSerializer(many=True)
    languages = LanguageSerializer(many=True)

    class Meta:
        model = CV
        fields = ['user', 'first_name', 'last_name', 'email', 'date_of_birth', 'hobbies',
                  'phone_number', 'schools', 'experiences', 'skills', 'languages']

    def create(self, validated_data):
        cv_data = validated_data.pop('cv')
        try:
            validate_international_phonenumber(cv_data['phone_number'])
        except ValidationError:
            print(cv_data['phone_number'])
            raise serializers.ValidationError({'phone_number': 'Phone number is invalid'})

        cv = super(CVSerializer, self).create(validated_data)
        cv, wasCreated = self.update_or_create_account(cv, cv_data)

        cv.save()
        return cv

    def update(self, instance, validated_data):
        cv_data = validated_data.pop('cv', None)
        self.update_or_create_account(instance, cv_data)
        return super(CVSerializer, self).update(instance, validated_data)

    def update_or_create_account(self, user, cv_data):
        return CV.objects.update_or_create(user=user, defaults=cv_data)
