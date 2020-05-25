from .models import *
from rest_framework import serializers


class PhotoLayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoLayer
        fields = '__all__'


class TileSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False)
    photo_layer = PhotoLayerSerializer()

    class Meta:
        model = Tile
        fields = ['id', 'title', 'destination', 'color', 'photo_layer', 'photo']
