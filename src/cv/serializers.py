from rest_framework import serializers
from django.contrib.auth.models import User
from phonenumber_field.validators import validate_international_phonenumber
from django.core.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField

from .models import *

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['name', 'year_start', 'year_end', 'additional_info']


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


class BasicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicInfo
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'phone_number']


class CVSerializer(serializers.ModelSerializer):
    basic_info = BasicInfoSerializer(read_only=True)
    schools = SchoolSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    user_id = serializers.IntegerField()
    class Meta:
        model = CV
        fields = ['user_id', 'basic_info', 'schools', 'experiences', 'skills', 'languages']

    def create(self, validated_data):
        cv_data = validated_data.pop('cv', None)
        if not CV.objects.filter(user_id=validated_data['user_id']).exists():
            cv = super(CVSerializer, self).create(validated_data)
            cv, wasCreated = self.update_or_create_cv(cv, cv_data)
            cv.save()
            return cv
        else:
            self.update(CV.objects.get(user_id=validated_data['user_id']), validated_data)
            return self

    def update(self, instance, validated_data):
        cv_data = validated_data.pop('cv', None)
        self.update_or_create_cv(instance.user_id, cv_data)
        return super(CVSerializer, self).update(instance, validated_data)

    def update_or_create_cv(self, user_id, cv_data):
        return CV.objects.update_or_create(user_id=user_id, defaults=cv_data)
