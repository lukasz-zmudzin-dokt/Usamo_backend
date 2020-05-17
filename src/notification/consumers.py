from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer, WebsocketConsumer
from channels_redis.core import logger
from rest_framework.authtoken.models import Token


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        await self.channel_layer.group_add(
            user.username,
            self.channel_name,
        )
        await self.accept(self.scope['subprotocols'][0])

    async def websocket_disconnect(self, event):
        try:
            user = self.scope['user']

            # Get the group from which user is to be kicked.
            group_name = user.username

            # kick this channel from the group.
            await self.channel_layer.group_discard(group_name, self.channel_name)
        except Exception as e:
            logger.error(e)

    async def new_notification(self, event):
        await self.send(text_data=event['event'])