from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notifications.models import Notification
from chat.models import ChatMessage
from chat.serializers import ChatMessageSerializer
from notification.serializers import NotificationSerializer


@receiver(post_save, sender=Notification)
def announce_new_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            instance.recipient.username, {
                "event": "Nowe powiadomienie",
                "type": "new_notification",
                "data": NotificationSerializer(instance=instance).data
            }
        )