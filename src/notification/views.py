from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import views, generics, status

from account.models import Account
from job.views import MessageResponse, ErrorResponse
from notification.serializers import *
from notification.jobs import start_scheduler, stop_scheduler


def slug2id(slug):
    return int(slug) - 110909


class NotificationsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class AllNotifications(generics.ListAPIView):
    serializer_class = NotificationSerializer
    pagination_class = NotificationsPagination

    def get_queryset(self):
        return self.request.user.notifications.all()


class UnreadNotifications(generics.ListAPIView):
    serializer_class = NotificationSerializer
    pagination_class = NotificationsPagination

    def get_queryset(self):
        return self.request.user.notifications.unread()


class UnreadNotificationsCount(views.APIView):
    @swagger_auto_schema(
        responses={
            '200': '"unread_count": int',
            '403': 'Nie podano danych uwierzytelniających.',
        },
        operation_description='Zwraca liczbę nieprzeczytanych powiadomień danego użytkownika'
    )
    def get(self, request):
        return Response({"unread_count": self.request.user.notifications.unread().count()}, status=status.HTTP_200_OK)


class MarkAsRead(views.APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('slug', openapi.IN_PATH, type='integer',
                              description='Liczba slug będąca identyfikatorem powiadomienia')
        ],
        responses={
            '200': '"message": Oznaczono powiadomienie jako przeczytane/nieprzeczytane',
            '403': 'Nie podano danych uwierzytelniających.',
            '404': 'Nie ma takiego powiadomienia!'
        },
        operation_description='Ustawia status powiadomienia na'
                              ' przeczytane lub nieprzeczytane, zależnie od stanu pierwotnego'
    )
    def post(self, request, slug):
        try:
            instance = request.user.notifications.get(id=slug2id(slug))
        except Notification.DoesNotExist:
            return ErrorResponse('Nie ma takiego powiadomienia!', status.HTTP_404_NOT_FOUND)
        if instance.unread:
            instance.mark_as_read()
            return MessageResponse('Oznaczono powiadomienie jako przeczytane')
        else:
            instance.mark_as_unread()
            return MessageResponse('Oznaczono powiadomienie jako nieprzeczytane')


class MarkAllAsRead(views.APIView):
    @swagger_auto_schema(
        responses={
            '200': '"message": Oznaczono wszystkie powiadomienia jako przeczytane',
            '403': 'Nie podano danych uwierzytelniających.',
        },
        operation_description='Ustawia status wszystkich powiadomień użytkownika na przeczytane'
    )
    def post(self, request):
        request.user.notifications.mark_all_as_read()
        return MessageResponse('Oznaczono wszystkie powiadomienia jako przeczytane')


class Delete(views.APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('slug', openapi.IN_PATH, type='integer',
                              description='Liczba slug będąca identyfikatorem powiadomienia')
        ],
        responses={
            '200': '"message": Pomyślnie usunięto powiadomienie',
            '403': 'Nie podano danych uwierzytelniających.',
            '404': 'Nie ma takiego powiadomienia!'
        },
        operation_description='Usuwa wybrane powiadomienie użytkownika'
    )
    def delete(self, request, slug):
        try:
            instance = request.user.notifications.get(id=slug2id(slug))
        except Notification.DoesNotExist:
            return ErrorResponse('Nie ma takiego powiadomienia!', status.HTTP_404_NOT_FOUND)
        instance.delete()
        return MessageResponse('Pomyślnie usunięto powiadomienie!')


class DeleteAll(views.APIView):
    @swagger_auto_schema(
        responses={
            '200': '"message": Usunięto wszystkie twoje powiadomienia!',
            '403': 'Nie podano danych uwierzytelniających.',
        },
        operation_description='Usuwa wszystkie powiadomienia użytkownika'
    )
    def delete(self, request):
        request.user.notifications.all().delete()
        return MessageResponse('Usunięto wszystkie twoje powiadomienia!')


class StartDailyNotifications(views.APIView):
    @swagger_auto_schema(
        responses={
            '200': '"message": Powiadomienia będą wysyłane na adres mailowy codziennie o 06:00'
        },
        operation_description='Włącza dzienne podsumowania mailowe powiadomień'
    )
    def post(self, request):
        pk = request.user.id
        start_scheduler(pk)
        return MessageResponse('Powiadomienia będą wysyłane na adres mailowy codziennie o 06:00')


class StopDailyNotifications(views.APIView):
    @swagger_auto_schema(
        responses={
            '200': '"message": Powiadomienia nie będą już wysyłane na adres mailowy'
        },
        operation_description='Wyłącza dzienne podsumowania mailowe powiadomień'
    )
    def post(self, request):
        pk = request.user.id
        stop_scheduler(pk)
        return MessageResponse('Powiadomienia nie będą już wysyłane na adres mailowy')


class SubscribeToWS(views.APIView):
    permission_classes = (AllowAny, )

    def get(self, request):
        return MessageResponse('Nawiązano kontakt z WebSocketem')
