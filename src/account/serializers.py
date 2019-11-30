from rest_framework import serializers
from django.contrib.auth.models import User
from phonenumber_field.validators import validate_international_phonenumber
from django.core.exceptions import ValidationError
from .models import Account


class UserSerializer(serializers.ModelSerializer):

    confirmed_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    phone_number = serializers.CharField(source='account.phone_number')

    class Meta:
        model = User
        fields = ['email', 'username', 'last_name', 'first_name', 'password', 'confirmed_password', 'phone_number']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):

        print(validated_data)

        password = validated_data.pop('password')
        confirmed_password = validated_data.pop('confirmed_password')

        if password != confirmed_password:
            raise serializers.ValidationError({'password': 'Passwords must be equal'})

        account_data = validated_data.pop('account', None)
        try:
            validate_international_phonenumber(account_data['phone_number'])
        except ValidationError:
            print(account_data['phone_number'])
            raise serializers.ValidationError({'phone_number': 'Phone number is invalid'})

        user = super(UserSerializer, self).create(validated_data)
        self.update_or_create_account(user, account_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        account_data = validated_data.pop('account', None)
        self.update_or_create_account(instance, account_data)
        return super(UserSerializer, self).update(instance, validated_data)

    def update_or_create_account(self, user, account_data):
        Account.objects.update_or_create(user=user, defaults=account_data)
