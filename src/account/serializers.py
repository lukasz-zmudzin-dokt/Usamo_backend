import abc
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import serializers
import abc
from .validators import validate_nip, validate_postal_code, validate_street_number
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from .account_type import StaffGroupType, ACCOUNT_TYPE_CHOICES
from .models import DefaultAccount, EmployerAccount, Account, StaffAccount, Address
from .account_type import STAFF_GROUP_CHOICES
from .models import DefaultAccount, EmployerAccount, Account, StaffAccount
from .validators import validate_nip


class AbstractAccountSerializer(serializers.ModelSerializer):

    picture_url = serializers.CharField(read_only=True)

    def create(self, validated_data):
        password = validated_data.pop('password')
        account_data = self.get_account_data(validated_data)

        try:
            validate_password(password)
        except ValidationError as e:
            errors = {}
            errors['password'] = list(e.messages)
            raise serializers.ValidationError(errors)
        
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
        self.post_user_saved(user)
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
            raise serializers.ValidationError(
                {'phone_number': 'Numer telefonu jest nieprawidłowy'})

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

    @abc.abstractmethod
    def post_user_saved(self, user):
        return


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['city', 'street', 'street_number', 'postal_code']

    def validate(self, attrs):
        postal_code = attrs['postal_code']
        street_number = attrs['street_number']
        try:
            validate_postal_code(postal_code)
            validate_street_number(street_number)
            return super().validate(attrs)
        except ValidationError as err:
            raise serializers.ValidationError(err.message)


class DefaultAccountSerializer(AbstractAccountSerializer):
    facility_address = AddressSerializer(source='account.facility_address')
    facility_name = serializers.CharField(source='account.facility_name')
    phone_number = serializers.CharField(source='account.phone_number')

    class Meta:
        model = Account
        fields = ['email', 'username', 'last_name', 'first_name',
                  'password', 'phone_number', 'facility_name', 'facility_address', 'picture_url']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'last_name': {'required': True},
            'phone_number': {'required': True},
            'first_name': {'required': True},
            'facility_name': {'required': True},
            'facility_address': {'required': True},
        }

    def update(self, instance, validated_data):
        account_data = validated_data.pop('account', None)
        self.update_or_create_account(instance, account_data)
        return super(DefaultAccountSerializer, self).update(instance, validated_data)

    def update_or_create_account(self, user, account_data):
        address = account_data.pop('facility_address')
        address_created = Address.objects.create(**address)
        return DefaultAccount.objects.update_or_create(user=user, defaults=account_data, facility_address=address_created)

    def perform_additional_validation(self, data):
        try:
            super(DefaultAccountSerializer, self)._validate_phone_number(
                data['phone_number'])
        except ValidationError as error:
            raise error

    def get_account_data(self, validated_data):
        return validated_data.pop('account', None)

    def post_user_created(self, user, data):
        pass

    def post_user_saved(self, user):
        pass


class EmployerAccountSerializer(AbstractAccountSerializer):
    company_address = AddressSerializer(source='employer_account.company_address')
    company_name = serializers.CharField(source='employer_account.company_name')
    nip = serializers.CharField(source='employer_account.nip')
    phone_number = serializers.CharField(source='employer_account.phone_number')

    class Meta:
        model = Account
        fields = ['email', 'username', 'last_name', 'first_name',
                  'password', 'phone_number', 'company_name', 'company_address', 'nip', 'picture_url']
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
        address = account_data.pop('company_address')
        address_created = Address.objects.create(**address)
        return EmployerAccount.objects.update_or_create(user=user, defaults=account_data, company_address=address_created)

    def perform_additional_validation(self, data):
        try:
            super(EmployerAccountSerializer, self)._validate_phone_number(
                data['phone_number'])
            self.__validate_nip(data['nip'])
        except ValidationError as error:
            raise error

    def get_account_data(self, validated_data):
        return validated_data.pop('employer_account', None)

    def post_user_created(self, user, data):
        pass

    def post_user_saved(self, user):
        pass


class GroupsField(serializers.MultipleChoiceField):

    def to_representation(self, value):
        return list(super().to_representation(value))


class StaffAccountSerializer(AbstractAccountSerializer):
    group_type = GroupsField(choices=STAFF_GROUP_CHOICES, required=True)

    class Meta:
        model = Account
        fields = ['email', 'username', 'last_name',
                  'first_name', 'password', 'group_type', 'picture_url']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'last_name': {'required': True},
            'first_name': {'required': True}
        }

    def update_or_create_account(self, user, account_data):
        return StaffAccount.objects.update_or_create(user=user, defaults=account_data)

    def perform_additional_validation(self, data):
        pass

    def get_account_data(self, validated_data):
        return validated_data.pop('staff_account', None)

    @staticmethod
    def __add_to_group(user, groups):
        for i in groups:
            group, created = Group.objects.get_or_create(name=i)
            user.groups.add(group)

    def post_user_created(self, user, data):
        self.__add_to_group(user, self.initial_data['group_type'])
        pass

    def post_user_saved(self, user):
        pass

    def validate(self, attrs):
        attrs.pop('group_type', None)
        return attrs


class AccountListSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')
    status = serializers.CharField(source='get_status_display')
    
    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 'type',
                  'date_joined', 'last_login', 'status', 'picture_url']


class EmployerDetailSerializer(EmployerAccountSerializer, AccountListSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'phone_number', 'company_name', 'company_address',
                  'nip', 'date_joined', 'last_login', 'status', 'picture_url']


class StaffDetailSerializer(StaffAccountSerializer, AccountListSerializer):
    group_type = serializers.ReadOnlyField()

    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'group_type',
                  'date_joined', 'last_login', 'status', 'picture_url']


class DefaultAccountDetailSerializer(DefaultAccountSerializer, AccountListSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'phone_number', 'facility_name', 'facility_address',
                  'date_joined', 'last_login', 'status', 'picture_url']


class ProfilePictureSerializer(serializers.Serializer):

    picture = serializers.ImageField()

    def update(self, instance, validated_data):
        return self.__update_or_create_profile_picture(validated_data)

    def create(self, validated_data):
        return self.__update_or_create_profile_picture(validated_data)

    def __update_or_create_profile_picture(self, validated_data):
        user = self.context['user']
        user.delete_image_if_exists()
        user.profile_picture = validated_data['picture']
        user.save()
        return user
