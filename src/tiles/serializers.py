from .models import *
from rest_framework import serializers


class PhotoLayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoLayer
        fields = ['left', 'top', 'right']


class TileSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False)
    photo_layer = PhotoLayerSerializer(required=False)

    class Meta:
        model = Tile
        fields = ['id', 'title', 'destination', 'color', 'photo_layer', 'photo']

    def create(self, validated_data):
        if validated_data.get('photo_layer') is not None:
            validated_data['photo_layer'] = PhotoLayer.objects.create(**validated_data['photo_layer'])
            tile = Tile(**validated_data)
            tile.save()
        else:
            tile = Tile(**validated_data)
            photo_layer = PhotoLayer.objects.create()
            photo_layer.save()
            tile.photo_layer = photo_layer
            tile.save()

        return tile

    def update(self, instance, validated_data):
        if 'photo_layer' in validated_data:
            serializer = PhotoLayerSerializer()
            serializer.update(instance.photo_layer, validated_data['photo_layer'])
        if 'title' in validated_data:
            instance.title = validated_data.get('title', instance.title)
        if 'destination' in validated_data:
            instance.destination = validated_data.get('destination', instance.destination)
        if 'color' in validated_data:
            instance.color = validated_data.get('color', instance.color)

        instance.save()
        return instance