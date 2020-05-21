from rest_framework import serializers
from .models import *


class PhoneContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneContact
        fields = ['id', 'title', 'description', 'phone_number']
        read_only_fields = ['id']

    def create(self, validated_data):
        return PhoneContact.objects.create(**validated_data)
