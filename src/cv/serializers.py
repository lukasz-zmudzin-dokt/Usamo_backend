from rest_framework import serializers
from django.contrib.auth.models import User
from phonenumber_field.validators import validate_international_phonenumber
from django.core.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField
from django.core.files.base import ContentFile
from .utilities import *
from .models import *
from account.models import DefaultAccount


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
    picture = serializers.ImageField(required=False)

    class Meta:
        model = BasicInfo
        fields = ['first_name', 'last_name', 'email',
                  'date_of_birth', 'phone_number', 'picture']


class FeedbackSerializer(serializers.ModelSerializer):
    cv_id = serializers.UUIDField()

    class Meta:
        model = Feedback
        fields = ['cv_id', 'basic_info', 'schools', 'experiences',
                  'skills', 'languages', 'additional_info']

    def create(self, validated_data):
        if Feedback.objects.filter(cv_id=validated_data['cv_id']).exists():
            fb = super().update(Feedback.objects.get(
                cv_id=validated_data['cv_id']), validated_data)
        else:
            fb = super().create(validated_data)
        cv = CV.objects.get(cv_id=validated_data['cv_id'])
        cv.is_verified = True
        cv.save()
        fb.save()
        return fb


class CVDataSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source='cv_user.user.id')
    basic_info = BasicInfoSerializer()
    schools = SchoolSerializer(many=True)
    experiences = ExperienceSerializer(many=True, required=False)
    skills = SkillSerializer(many=True)
    languages = LanguageSerializer(many=True)
    is_verified = serializers.BooleanField(default=False)

    class Meta:
        model = CV
        fields = ['cv_id', 'user_id', 'basic_info', 'schools', 'experiences', 'skills',
                  'languages', 'wants_verification', 'is_verified']


class CVSerializer(serializers.ModelSerializer):
    cv_id = serializers.UUIDField()
    basic_info = BasicInfoSerializer()
    schools = SchoolSerializer(many=True)
    experiences = ExperienceSerializer(many=True, required=False)
    skills = SkillSerializer(many=True)
    languages = LanguageSerializer(many=True)
    is_verified = serializers.BooleanField(default=False)

    class Meta:
        model = CV
        fields = ['cv_id', 'cv_user', 'basic_info', 'schools', 'experiences', 'skills',
                  'languages', 'wants_verification', 'is_verified']
        
        extra_kwargs = {
            'cv_id': {'required': True},
            'cv_user': {'required': True},
            'basic_info': {'required': True},
            'schools': {'required': True},
            'experiences': {'required': False},
            'skills': {'required': True},
            'languages': {'required': True},
            'wants_verification': {'required': False},
            'is_verified': {'required': False}
        }

    def create(self, validated_data):
        if CV.objects.filter(cv_id=validated_data['cv_id']).exists():
            cv = self.update(CV.objects.all().get(
                cv_id=validated_data['cv_id']), validated_data)
        else:
            pdf = generate(validated_data)
            django_file = ContentFile(pdf)
            django_file.name = create_unique_filename('cv_docs', 'pdf')
            cv = CV.objects.create(
                cv_id=validated_data['cv_id'], cv_user=validated_data['cv_user'], wants_verification=True, 
                    is_verified=False, document=django_file)
            basic_info_data = validated_data.pop('basic_info')
            BasicInfo.objects.create(cv=cv, **basic_info_data)
        return self.create_lists(cv, validated_data)

    def update(self, cv, validated_data):
        basic_info_data = validated_data.get('basic_info')
        serializer = BasicInfoSerializer()
        serializer.update(cv.basic_info, basic_info_data)
        School.objects.filter(cv=cv).delete()
        Experience.objects.filter(cv=cv).delete()
        Skill.objects.filter(cv=cv).delete()
        Language.objects.filter(cv=cv).delete()
        cv.wants_verification = True
        cv.is_verified = False

        validated_data['basic_info']['picture'] = cv.basic_info.picture
        pdf = generate(validated_data)
        django_file = ContentFile(pdf)
        django_file.name = create_unique_filename('cv_docs', 'pdf')
        cv.document = django_file
        cv.save()
        return cv

    @staticmethod
    def create_lists(cv, validated_data):
        schools_data = validated_data.pop('schools')
        try:
            experiences_data = validated_data.pop('experiences')
        except KeyError:
            experiences_data = False
        skills_data = validated_data.pop('skills')
        languages_data = validated_data.pop('languages')

        for data in schools_data:
            School.objects.create(cv=cv, **data)

        if experiences_data:
            for data in experiences_data:
                Experience.objects.create(cv=cv, **data)

        for data in skills_data:
            Skill.objects.create(cv=cv, **data)

        for data in languages_data:
            Language.objects.create(cv=cv, **data)

        return cv
