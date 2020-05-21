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
        user = super(AbstractAccountSerializer, self).create(validated_data)
        self.post_user_created(user, validated_data)
        account, wasCreated = self.update_or_create_account(user, account_data)
        user.set_password(password)
        user.save()
        account.save()
        self.post_user_saved(user)
        return user

    def update(self, instance, validated_data):
        username = validated_data.get('username', instance.username)
        email = validated_data.get('email', instance.email)
        first_name = validated_data.get('first_name', instance.first_name)
        last_name = validated_data.get('last_name', instance.last_name)
        email = validated_data.get('email', instance.email)
        password = validated_data.get('password', None)

        if password is not None:
            instance.set_password(password)

        instance.username = username
        instance.email = email
        instance.first_name = first_name
        instance.last_name = last_name
        instance.save()
        return instance

    def validate(self, data):
        password = data.get('password', None)
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                errors = {}
                errors['password'] = list(e.messages)
                raise serializers.ValidationError(errors)
        return data

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
        postal_code = attrs.get('postal_code', None)
        street_number = attrs.get('street_number', None)
        if postal_code:
            try:
                validate_postal_code(postal_code)
            except ValidationError as err:
                raise serializers.ValidationError(err.message)
        if street_number:
            try:
                validate_street_number(street_number)    
            except ValidationError as err:
                raise serializers.ValidationError(err.message)

        return super().validate(attrs)            


class PasswordChangeRequestSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, data):       
        new_password = data['new_password']

        try:
            validate_password(new_password)
        except ValidationError as e:
            errors = {}
            errors['new_password'] = list(e.messages)
            raise serializers.ValidationError(errors)
        
        return super().validate(data)


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
        def_account = DefaultAccount.objects.get(user=instance)
        account_data = validated_data.pop('account', None)
        if account_data:
            new_address_data = account_data.pop('facility_address', None)
            if new_address_data:
                new_address = Address.objects.create(**new_address_data)
                def_account.facility_address.delete()
                def_account.facility_address = new_address
            phone_number = account_data.pop('phone_number', None)
            if phone_number:
                def_account.phone_number = phone_number
            facility_name = account_data.pop('facility_name', None)    
            if facility_name:
                def_account.facility_name = facility_name
            
            def_account.save()
        return super().update(instance, validated_data)

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

    def validate(self, data):
        account_data = data.get('account', None)
        if account_data:
            try:
                self.perform_additional_validation(account_data)
            except serializers.ValidationError as error:
                raise error
        return super().validate(data)

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

    def update(self, instance, validated_data):
        employer_account = EmployerAccount.objects.get(user=instance)
        account_data = validated_data.pop('employer_account', None)
        if account_data:
            new_address_data = account_data.pop('company_address', None)
            if new_address_data:
                new_address = Address.objects.create(**new_address_data)
                employer_account.company_address.delete()
                employer_account.company_address = new_address
            phone_number = account_data.pop('phone_number', None)
            if phone_number:
                employer_account.phone_number = phone_number
            company_name = account_data.pop('company_name', None)    
            if company_name:
                employer_account.company_name = company_name
            nip = account_data.pop('nip', None)    
            if nip:
                employer_account.nip = nip
            
            employer_account.save()
        return super().update(instance, validated_data) 

    def perform_additional_validation(self, data):
        phone_number = data.get('phone_number', None)
        nip = data.get('nip', None)
        try:
            if phone_number:
                super(EmployerAccountSerializer, self)._validate_phone_number(
                    data['phone_number'])
            if nip:
                self.__validate_nip(data['nip'])
        except ValidationError as error:
            raise error

    def validate(self, data):
        account_data = data.get('employer_account', None)
        if account_data:
            try:
                self.perform_additional_validation(account_data)
            except serializers.ValidationError as error:
                raise error
        return super().validate(data)

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

    def update(self, instance, validated_data):
        validated_data.pop('group_type', None)
        validated_data.pop('password', None)
        return super().update(instance, validated_data) 

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
        return super().validate(attrs)


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
