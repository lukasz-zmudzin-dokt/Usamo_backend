from django.contrib.auth import get_user_model
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Thread, ChatMessage
from django.contrib.auth.models import AnonymousUser
from account.models import Account
import json
from django.utils import timezone
from .serializers import ThreadSerializer
from notifications.signals import notify


class ChatConsumer(AsyncJsonWebsocketConsumer):
    
    async def connect(self):
        try:        
            other_user = self.scope['url_route']['kwargs']['username']
            this_user = self.scope['user'].username 
            thread_obj = await self.get_thread(this_user, other_user)
            
            if thread_obj is not None:
                chat_room = thread_obj.room_name
                self.chat_room = chat_room
                self.thread_obj = thread_obj
                await self.channel_layer.group_add(self.chat_room, self.channel_name)
                await self.accept(self.scope['subprotocols'][0])
            else: 
                await self.close()
        except Account.DoesNotExist:
            await self.close()

    async def receive_json(self, content):
        msg = content.get("message", None)
        recipient_username = content.get("recipient", None)
        try:
            this_user = self.scope['user']
            instance = await self.create_chat_message(msg, recipient_username)
            response = {
                "message": msg,
                "username": this_user.username,
                "first_name": this_user.first_name,
                "last_name": this_user.last_name,
                "timestamp": instance.timestamp.__str__()
            }
            
            await self.channel_layer.group_send(
                self.chat_room, 
                {
                    "type": "chat.message",
                    "text": json.dumps(response)
                }
            )
        except Exception:
            self.close()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.chat_room, self.channel_name)
        except AttributeError:
            pass 

    async def chat_message(self, event):
        await self.send_json(event['text'])  
        

    @database_sync_to_async
    def get_thread(self, this_user, other_user):
        return Thread.objects.get_or_new(this_user, other_user)[0]

    @database_sync_to_async
    def create_chat_message(self, msg, username):
        sender = self.scope['user']
        try:
            recipient = Account.objects.get(username=username)
        except Account.DoesNotExist as e:
            raise e
        notify.send(sender, recipient=recipient, verb=f'Nowa wiadomość od: {sender.first_name} {sender.last_name}',
            app='chat', object_id=self.thread_obj.id)

        self.thread_obj.updated = timezone.now()
        self.thread_obj.save()
        return ChatMessage.objects.create(thread=self.thread_obj, sender=self.scope['user'], recipient=recipient, message=msg)


class InboxConsumer(AsyncJsonWebsocketConsumer):
    
    async def connect(self):   
        if self.scope['user'].is_anonymous:
            await self.close()
        else: 
            self.user = self.scope['user']
            await self.accept(self.scope['subprotocols'][0])
                  
    async def receive_json(self, content):
        msg = content.get("message", None)
        if msg == 'threads':
            threads = await self.get_threads()
            serializer = ThreadSerializer(threads, many=True)

            await self.send_json(serializer.data)
        
        else:
            await self.close()

    async def disconnect(self, close_code):
        pass 

    @database_sync_to_async
    def get_threads(self):
        return Thread.objects.by_user(self.user)