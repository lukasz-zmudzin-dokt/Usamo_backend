from rest_framework import serializers
from .models import *


class PhoneContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneContact
        fields = '__all__'
