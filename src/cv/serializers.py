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
    basic_info = BasicInfoSerializer(many=False)
    schools = SchoolSerializer(many=True)
    experiences = ExperienceSerializer(many=True)
    skills = SkillSerializer(many=True)
    languages = LanguageSerializer(many=True)
    cv_id = serializers.IntegerField()

    class Meta:
        model = CV
        fields = ['cv_id', 'basic_info', 'schools', 'experiences', 'skills', 'languages']
        depth = 2

    def create(self, validated_data):
        if not CV.objects.filter(cv_id=validated_data['cv_id']).exists():
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

        else:
            cv = self.update(CV.objects.get(cv_id=validated_data['cv_id']), validated_data)
            return cv

    def update(self, cv, validated_data):
        ''' instance.basic_info = validated_data['basic_info']
        instance.schools = validated_data['schools']
        instance.experiences = validated_data['experiences']
        instance.skills = validated_data['skills']
        instance.languages = validated_data['languages']'''
        basic_info_data = validated_data.pop('basic_info')
        schools_data = validated_data.pop('schools')
        experiences_data = validated_data.pop('experiences')
        skills_data = validated_data.pop('skills')
        languages_data = validated_data.pop('languages')
        BasicInfo.objects.update(cv=cv, **basic_info_data)

        for school_data in schools_data:
            School.objects.update(cv=cv, **school_data)

        for experience_data in experiences_data:
            Experience.objects.update(cv=cv, **experience_data)

        for skill_data in skills_data:
            Skill.objects.update(cv=cv, **skill_data)

        for language_data in languages_data:
            Language.objects.update(cv=cv, **language_data)

        return cv

    def update_or_create_cv(self, user_id, cv_data):
        return CV.objects.update_or_create(defaults=cv_data)
