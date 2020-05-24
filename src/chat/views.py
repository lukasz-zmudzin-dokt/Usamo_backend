from rest_framework import status
from rest_framework import views
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from account.permissions import IsStaffWithChatAccess, IsEmployer, IsStandardUser
from account.serializers import StaffAccountSerializer, AccountListSerializer
from account.account_type import AccountType, StaffGroupType
from account.account_status import AccountStatus
from account.models import Account
from django.contrib.auth.models import Group
from .serializers import *
from .models import *
from job.views import ErrorResponse, MessageResponse, sample_error_response, sample_message_response
from django.db.models import Q


class InboxView(ListAPIView):
    serializer_class = ThreadSerializer
    permission_classes = (IsStaffWithChatAccess | IsEmployer | IsStandardUser, )
    # filter_backends = (DjangoFilterBackend, UserListOrderingFilter,)
    # filterset_class = DefaultAccountListFilter
    # ordering_fields = ['username', 'date_joined', 'last_login']
    # ordering = ['-date_joined']

    def get_queryset(self):
        user = self.request.user
        return Thread.objects.by_user(user)


class ContactListView(ListAPIView):
    serializer_class = ThreadSerializer
    permission_classes = (IsStaffWithChatAccess | IsEmployer | IsStandardUser, )
    # filter_backends = (DjangoFilterBackend, UserListOrderingFilter,)
    # filterset_class = DefaultAccountListFilter
    # ordering_fields = ['username', 'date_joined', 'last_login']
    # ordering = ['-date_joined']

    def get_queryset(self):
        user = self.request.user
        qlookup = ~Q(status=AccountStatus.VERIFIED.value) | Q(username=user.username)
        group = Group.objects.filter(name=StaffGroupType.STAFF_CHAT_ACCESS.value)
        qlookup2 = ~Q(type=AccountType.STAFF.value) | Q(groups__in=group) 
        qlookup3 = Q(type=AccountType.STAFF.value) & Q(groups__in=group) 

        if user.type == AccountType.STAFF.value:
            return Account.objects.filter(qlookup2).exclude(qlookup)

        return Account.objects.filter(qlookup3)

    def get_serializer_class(self):
        user = self.request.user
        if user.type == AccountType.STAFF.value:
            return ChatUserSerializer

        return StaffAccountSerializer  


class ThreadView(ListAPIView):
    permission_classes = (IsStaffWithChatAccess | IsEmployer | IsStandardUser, )
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        user = self.request.user
        other_username = self.kwargs['username']
        qlookup1 = Q(first__username=user.username) & Q(second__username=other_username)
        qlookup2 = Q(first__username=other_username) & Q(second__username=user.username)

        thread = Thread.objects.filter(qlookup1 | qlookup2).first()
        return ChatMessage.objects.filter(thread=thread.id)