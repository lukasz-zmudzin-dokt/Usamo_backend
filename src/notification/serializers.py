from rest_framework import serializers
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    data = serializers.DictField(write_only=True)
    text = serializers.CharField(source='data.text', required=False)
    app = serializers.CharField(source='data.app', required=False)
    object_id = serializers.CharField(source='data.object_id', required=False)
    slug = serializers.CharField(read_only=True)
    unread = serializers.BooleanField(read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Notification
        fields = ['slug', 'data', 'text', 'app', 'object_id', 'unread', 'timestamp']