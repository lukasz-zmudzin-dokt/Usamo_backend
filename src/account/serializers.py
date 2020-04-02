from django.core.exceptions import ValidationError
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import serializers
import abc
from .validators import validate_nip
from django.contrib.auth.models import Group
from .account_type import StaffGroupType


from .models import DefaultAccount, EmployerAccount, Account, StaffAccount


class AbstractAccountSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        password = validated_data.pop('password')
        account_data = self.get_account_data(validated_data)
        try:
            self.perform_additional_validation(account_data)
        except serializers.ValidationError as error:
            raise error

        user = super(AbstractAccountSerializer, self).create(validated_data)
        self.post_user_created(user, validated_data)
        account, wasCreated = self.update_or_create_account(user, account_data)
        user.set_password(password)
        user.save()
        account.save()
        return user

    def update(self, instance, validated_data):
        account_data = validated_data.pop('account', None)
        self.update_or_create_account(instance, account_data)
        return super(AbstractAccountSerializer, self).update(instance, validated_data)

    @staticmethod
    def _validate_phone_number(phone_number):
        try:
            validate_international_phonenumber(phone_number)
        except ValidationError:
            raise serializers.ValidationError({'phone_number': 'Phone number is invalid'})

    @abc.abstractmethod
    def update_or_create_account(self, user, account_data):
        return

    @abc.abstractmethod
    def perform_additional_validation(self, data):
        return

    @abc.abstractmethod
    def get_account_data(self, validated_data):
        return

    @abc.abstractmethod
    def post_user_created(self, user, data):
        return


class DefaultAccountSerializer(AbstractAccountSerializer):
    facility_address = serializers.CharField(source='account.facility_address')
    facility_name = serializers.CharField(source='account.facility_name')
    phone_number = serializers.CharField(source='account.phone_number')

    class Meta:
        model = Account
        fields = ['email', 'username', 'last_name', 'first_name',
                  'password', 'phone_number', 'facility_name', 'facility_address']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'last_name': {'required': True},
            'phone_number': {'required': True},
            'first_name': {'required': True},
            'facility_name': {'required': True},
            'facility_address': {'required': True}
        }

    def update(self, instance, validated_data):
        account_data = validated_data.pop('account', None)
        self.update_or_create_account(instance, account_data)
        return super(DefaultAccountSerializer, self).update(instance, validated_data)

    def update_or_create_account(self, user, account_data):
        return DefaultAccount.objects.update_or_create(user=user, defaults=account_data)

    def perform_additional_validation(self, data):
        try:
            super(DefaultAccountSerializer, self)._validate_phone_number(data['phone_number'])
        except ValidationError as error:
            raise error

    def get_account_data(self, validated_data):
        return validated_data.pop('account', None)

    def post_user_created(self, user, data):
        pass


class EmployerAccountSerializer(AbstractAccountSerializer):
    company_address = serializers.CharField(source='employer_account.company_address')
    company_name = serializers.CharField(source='employer_account.company_name')
    nip = serializers.CharField(source='employer_account.nip')
    phone_number = serializers.CharField(source='employer_account.phone_number')

    class Meta:
        model = Account
        fields = ['email', 'username', 'last_name', 'first_name',
                  'password', 'phone_number', 'company_name', 'company_address', 'nip']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'last_name': {'required': True},
            'phone_number': {'required': True},
            'first_name': {'required': True},
            'company_name': {'required': True},
            'company_address': {'required': True},
            'nip': {'required': True}
        }

    @staticmethod
    def __validate_nip(nip):
        try:
            validate_nip(nip)
        except ValidationError as error:
            raise serializers.ValidationError({'nip': error.message})

    def update_or_create_account(self, user, account_data):
        return EmployerAccount.objects.update_or_create(user=user, defaults=account_data)

    def perform_additional_validation(self, data):
        try:
            super(EmployerAccountSerializer, self)._validate_phone_number(data['phone_number'])
            self.__validate_nip(data['nip'])
        except ValidationError as error:
            raise error

    def get_account_data(self, validated_data):
        return validated_data.pop('employer_account', None)

    def post_user_created(self, user, data):
        pass


class StaffAccountSerializer(AbstractAccountSerializer):

    type = serializers.ChoiceField(choices={i: i for i in StaffGroupType.get_all_types()}, write_only=True)

    groups = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['email', 'username', 'last_name', 'first_name', 'password', 'type', 'groups']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'last_name': {'required': True},
            'first_name': {'required': True},
            'type': {'required': True}
        }

    def get_groups(self, user):
        groups = user.groups.values_list('name', flat=True)
        return list(groups)

    def update_or_create_account(self, user, account_data):
        return StaffAccount.objects.update_or_create(user=user, defaults=account_data)

    def perform_additional_validation(self, data):
        pass

    def get_account_data(self, validated_data):
        return validated_data.pop('staff_account', None)

    @staticmethod
    def __add_to_group(user, group_type):
        group, created = Group.objects.get_or_create(name=group_type)
        user.groups.add(group)

    def post_user_created(self, user, data):
        self.__add_to_group(user, self.type)

    def validate(self, attrs):
        self.type = attrs['type']
        attrs.pop('type', None)
        return attrs
