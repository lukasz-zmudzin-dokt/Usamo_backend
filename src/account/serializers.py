from django.core.exceptions import ValidationError
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import serializers
import abc
from .validators import validate_nip


from .models import DefaultAccount, EmployerAccount, Account


class AbstractAccountSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='account.phone_number')

    def create(self, validated_data):
        password = validated_data.pop('password')
        account_data = validated_data.pop('account', None)

        try:
            self.__validate_phone_number(account_data['phone_number'])
            self.perform_additional_validation(account_data)
        except serializers.ValidationError as error:
            raise error

        user = super(AbstractAccountSerializer, self).create(validated_data)
        account, wasCreated = self.update_or_create_account(user, account_data)
        user.set_password(password)
        user.save()
        account.save()
        return user

    def update(self, instance, validated_data):
        account_data = validated_data.pop('account', None)
        self.update_or_create_account(instance, account_data)
        return super(AbstractAccountSerializer, self).update(instance, validated_data)

    def __validate_phone_number(self, phone_number):
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


class DefaultAccountSerializer(AbstractAccountSerializer):
    facility_address = serializers.CharField(source='account.facility_address')
    facility_name = serializers.CharField(source='account.facility_name')

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
        return


class EmployerAccountSerializer(AbstractAccountSerializer):
    company_address = serializers.CharField(source='account.company_address')
    company_name = serializers.CharField(source='account.company_name')
    nip = serializers.CharField(source='account.nip')

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

    def update_or_create_account(self, user, account_data):
        return EmployerAccount.objects.update_or_create(user=user, defaults=account_data)

    def perform_additional_validation(self, data):
        try:
            validate_nip(data['nip'])
        except ValidationError as error:
            raise serializers.ValidationError({'nip': error.message})
