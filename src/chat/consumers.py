import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from .models import Thread, ChatMessage


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        other_user = self.scope['url_route']['kwargs']['username']
        this_user = self.scope['user']
        thread_obj = await self.get_thread(this_user, other_user)
        chat_room = f"thread_{thread_obj.id}"
        self.chat_room = chat_room
        self.thread_obj = thread_obj
        await self.channel_layer.group_add(chat_room, self.channel_name)

        await self.send({
            "type": "websocket.accept"
        })


    async def websocket_receive(self, event):
        msg = event.get('text', None)

        if msg is not None:
            dictionary = json.loads(msg)
            msg_content = dictionary.get('message')
            user = self.scope['user']

            response = {
                'message': msg,
                'username': user.username
            }
            await self.create_chat_message(msg)

            await self.channel_layer.group_send(
                self.chat_room,
                {
                    "type": "chat_message",
                    "text": json.dumps(response)
                }
            )

    async def websocket_disconnect(self, event):
        print("disconnected", event)

    async def chat_message(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        })

    @database_sync_to_async
    def get_thread(self, this_user, other_user):
        return Thread.objects.get_or_new(this_user, other_user)[0]

    @database_sync_to_async
    def create_chat_message(self, msg):
        return ChatMessage.objects.create(thread=self.thread_obj, user=self.scope['user'], message=msg)