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
from .filters import *
from job.views import ErrorResponse, MessageResponse, sample_error_response, sample_message_response
from django.db.models import Q
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class ChatPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class InboxView(ListAPIView):
    serializer_class = ThreadSerializer
    pagination_class = ChatPagination
    permission_classes = (IsStaffWithChatAccess | IsEmployer | IsStandardUser, )
    filter_backends = (OrderingFilter,)
    ordering = ['-updated']

    def get_queryset(self):
        user = self.request.user
        return Thread.objects.by_user(user)


@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[DjangoFilterDescriptionInspector],
    responses={
        200: ChatUserSerializer(many=True),
        2137: StaffAccountSerializer(many=True) 
    },
    operation_description="Zwraca listę dostępnych kontaktów (nie mylić z rozmowami). Paginacja jak wszędzie indziej.\n Zwraca zawsze 200 :)"
))
class ContactListView(ListAPIView):
    serializer_class = ThreadSerializer
    permission_classes = (IsStaffWithChatAccess | IsEmployer | IsStandardUser, )
    pagination_class = ChatPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = ContactListFilter
    ordering = ['first_name', 'last_name']

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
    filter_backends = (OrderingFilter,)
    ordering = ['timestamp']


    def get_queryset(self):
        user = self.request.user
        other_username = self.kwargs['username']
        qlookup1 = Q(first__username=user.username) & Q(second__username=other_username)
        qlookup2 = Q(first__username=other_username) & Q(second__username=user.username)

        thread = Thread.objects.filter(qlookup1 | qlookup2).first()
        return ChatMessage.objects.filter(thread=thread.id)