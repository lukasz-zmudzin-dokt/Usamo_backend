from .models import *
from rest_framework import serializers


class TileSerializer(serializers.ModelSerializer):
    photo = serializers.URLField(required=False)

    class Meta:
        model = Tile
        fields = '__all__'
