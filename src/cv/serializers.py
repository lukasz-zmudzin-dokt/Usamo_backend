from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import serializers
from django.core.files.base import ContentFile

from .templates.templates import TEMPLATES_CHOICES
from .utilities import *
from .models import *

import datetime


class EnhancedDatesSerializer(serializers.ModelSerializer):
    date_start = serializers.CharField()
    date_end = serializers.CharField(required=False)

    def validate_date_start(self, value):
        short_date_format = re.compile("([0-9]{2})-([0-9]{4})")
        short_date_match = re.match(short_date_format, value)
        if short_date_match:
            year = int(short_date_match.group(2))
            if year < 1990:
                raise ValidationError("Data startu musi być większa niż 1990")
            if year > current_year():
                raise ValidationError("Data startu nie może być większa niż aktualny rok")
        else:
            raise ValidationError("Niewłaściwy format daty startu, powinien być: MM-YYYY")
        return value

    def validate_date_end(self, value):
        if not value:
            return value
        short_date_format = re.compile("([0-9]{2})-([0-9]{4})")
        short_date_match = re.match(short_date_format, value)
        if short_date_match:
            year = int(short_date_match.group(2))
            if year < 1990:
                raise ValidationError("Data końca musi być większa niż 1990")
            if year > current_year():
                raise ValidationError("Data końca nie może być większa niż aktualny rok")
        else:
            raise ValidationError("Niewłaściwy format daty końca, powinien być: MM-YYYY")
        return value


class SchoolSerializer(EnhancedDatesSerializer):
    date_end = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = School
        fields = ['name', 'date_start', 'date_end', 'additional_info']


class ExperienceSerializer(EnhancedDatesSerializer):
    date_end = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Experience
        fields = ['title', 'description', 'date_start', 'date_end']


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

    def validate_phone_number(self, value):
        try:
            validate_international_phonenumber(value)
        except ValidationError as error:
            raise error
        return value

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
        cv.was_reviewed = True
        cv.save()
        fb.save()
        return fb


class CVSerializer(serializers.ModelSerializer):
    cv_id = serializers.UUIDField(read_only=True)
    user_id = serializers.UUIDField(source='cv_user.user.id', read_only=True)
    date_created = serializers.DateTimeField(read_only=True)
    basic_info = BasicInfoSerializer()
    schools = SchoolSerializer(many=True)
    experiences = ExperienceSerializer(many=True, required=False)
    skills = SkillSerializer(many=True)
    languages = LanguageSerializer(many=True)
    template = serializers.ChoiceField(choices=TEMPLATES_CHOICES, default='bisque')
    is_verified = serializers.BooleanField(default=False, read_only=True)
    was_reviewed = serializers.BooleanField(read_only=True)
    has_picture = serializers.BooleanField(read_only=True)

    class Meta:
        model = CV
        fields = ['cv_id', 'template', 'user_id', 'name', 'date_created', 'is_verified', 'was_reviewed', 'has_picture',
        'cv_user', 'basic_info', 'schools', 'experiences', 'skills', 'languages']
        
        extra_kwargs = {
            'cv_user': {'required': False, 'write_only': True},
            'basic_info': {'required': True},
            'schools': {'required': True},
            'experiences': {'required': False},
            'skills': {'required': True},
            'languages': {'required': True},
            'is_verified': {'required': False},
            'name': {'required': False},
        }

    def create(self, validated_data):
        template = validated_data.pop('template')
        pdf = generate(validated_data, template)
        django_file = ContentFile(pdf)
        django_file.name = create_unique_filename('cv_docs', 'pdf')
        name = None
        if 'name' in validated_data:
            name = validated_data['name']
        cv = CV.objects.create(cv_user=validated_data['cv_user'],
                               is_verified=False,
                               document=django_file,
                               name=name,
                               template=template)
        basic_info_data = validated_data.pop('basic_info')
        BasicInfo.objects.create(cv=cv, **basic_info_data)
        return self.create_lists(cv, validated_data)

    def update(self, cv, validated_data):
        basic_info_data = validated_data.get('basic_info')
        serializer = BasicInfoSerializer()
        serializer.update(cv.basic_info, basic_info_data)
        cv.is_verified = False
        cv.was_reviewed = False
        School.objects.filter(cv=cv).delete()
        Experience.objects.filter(cv=cv).delete()
        Language.objects.filter(cv=cv).delete()
        Skill.objects.filter(cv=cv).delete()
        self.create_lists(cv, validated_data)
        template = validated_data.get('template')
        validated_data['basic_info'] = cv.basic_info
        pdf = generate(validated_data, template)
        django_file = ContentFile(pdf)
        django_file.name = create_unique_filename('cv_docs', 'pdf')
        cv.document = django_file
        cv.save()
        return cv

    @staticmethod
    def create_lists(cv, validated_data):
        schools_data = validated_data.get('schools')
        try:
            experiences_data = validated_data.get('experiences')
        except KeyError:
            experiences_data = False
        skills_data = validated_data.get('skills')
        languages_data = validated_data.get('languages')

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
