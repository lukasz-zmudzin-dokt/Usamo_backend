from django.db import models
from django.conf import settings
from django.db import models
from django.db.models import Q
from account.models import Account
from account.permissions import IsStaffWithChatAccess
from account.account_type import AccountType
from account.account_status import AccountStatus
import uuid

class ThreadManager(models.Manager):
    def by_user(self, user):
        qlookup = Q(first=user) | Q(second=user)
        qlookup2 = Q(first=user) & Q(second=user)
        qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
        return qs

    def has_permissions(self, user1, user2):
        if user1.status != AccountStatus.VERIFIED.value or user2.status != AccountStatus.VERIFIED.value:
            return False
        if user1.type != AccountType.STAFF.value and user2.type != AccountType.STAFF.value:
            return False
        if not IsStaffWithChatAccess()._is_allowed_staff(user1) and not IsStaffWithChatAccess()._is_allowed_staff(user2):
            return False

        return True    

    def get_or_new(self, username, other_username): 
        if username == other_username:
            return None, False
          
        try:
            user1 = Account.objects.get(username=username)
            user2 = Account.objects.get(username=other_username)
        except Account.DoesNotExist as e:
            raise e

        if not self.has_permissions(user1, user2):
            return None, False    

        qlookup1 = Q(first__username=username) & Q(second__username=other_username)
        qlookup2 = Q(first__username=other_username) & Q(second__username=username)
        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()

        if qs.count() == 1:
            return qs.first(), False
        elif qs.count() > 1:
            return qs.order_by('timestamp').first(), False
        else:
            obj = self.model(first=user1, second=user2)
            obj.save()
            return obj, True

        return None, False


class Thread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='chat_thread_first')
    second = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='chat_thread_second')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    objects = ThreadManager()

    @property
    def room_name(self):
        return f'chat_{self.id}'

    def broadcast(self, msg=None):
        if msg is not None:
            broadcast_msg_to_chat(msg, group_name=self.room_name, user='admin')
            return True
        return False


class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(Account, verbose_name='sender', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
