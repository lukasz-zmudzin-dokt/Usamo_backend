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
    basic_info = BasicInfoSerializer()
    schools = SchoolSerializer(many=True)
    experiences = ExperienceSerializer(many=True)
    skills = SkillSerializer(many=True)
    languages = LanguageSerializer(many=True)

    class Meta:
        model = CV
        fields = ['cv_id', 'basic_info', 'schools', 'experiences', 'skills', 'languages']

    def create(self, validated_data):
        if CV.objects.filter(cv_id=validated_data['cv_id']).exists():
            CV.objects.get(cv_id=validated_data['cv_id']).delete()

        basic_info_data = validated_data.pop('basic_info')
        schools_data = validated_data.pop('schools')
        experiences_data = validated_data.pop('experiences')
        skills_data = validated_data.pop('skills')
        languages_data = validated_data.pop('languages')
        cv = CV.objects.create(**validated_data)

        BasicInfo.objects.create(cv=cv, **basic_info_data)

        for school_data in schools_data:
            School.objects.create(cv=cv, **school_data)

        for experience_data in experiences_data:
            Experience.objects.create(cv=cv, **experience_data)

        for skill_data in skills_data:
            Skill.objects.create(cv=cv, **skill_data)

        for language_data in languages_data:
            Language.objects.create(cv=cv, **language_data)

        return cv
