from rest_framework import serializers
from .models import *
from account.models import Account


class ChatUserSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')
    class Meta:
        model = Account
        fields = ['username', 'first_name', 'last_name', 'picture_url', 'type']


class MessageAuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ['username', 'first_name', 'last_name']        


class ThreadSerializer(serializers.ModelSerializer):
    first = ChatUserSerializer()
    second = ChatUserSerializer()

    class Meta:
        model = Thread
        fields = ['id', 'first', 'second', 'updated']


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = MessageAuthorSerializer()

    class Meta:
        model = ChatMessage
        fields = ['sender', 'message', 'timestamp']


class ThreadMessageListSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True)
    first = ChatUserSerializer()
    second = ChatUserSerializer()

    class Meta:
        model = Thread
        fields = ['id', 'first', 'second', 'messages', 'updated']
