from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import serializers

from .models import Account


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='account.phone_number')
    facility_address = serializers.CharField(source='account.facility_address')
    facility_name = serializers.CharField(source='account.facility_name')

    class Meta:
        model = User
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

    def create(self, validated_data):

        password = validated_data.pop('password')

        account_data = validated_data.pop('account', None)

        try:
            validate_international_phonenumber(account_data['phone_number'])
        except ValidationError:
            print(account_data['phone_number'])
            raise serializers.ValidationError({'phone_number': 'Phone number is invalid'})

        user = super(UserSerializer, self).create(validated_data)
        account, wasCreated = self.update_or_create_account(user, account_data)
        user.set_password(password)
        user.save()
        account.save()
        return user

    def update(self, instance, validated_data):
        account_data = validated_data.pop('account', None)
        self.update_or_create_account(instance, account_data)
        return super(UserSerializer, self).update(instance, validated_data)

    def update_or_create_account(self, user, account_data):
        return Account.objects.update_or_create(user=user, defaults=account_data)
