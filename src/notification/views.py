from django.shortcuts import render
from notifications.models import Notification
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import views, generics, status

from notification.serializers import *


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

    def get(self, request):
        return Response({"unread_count": self.request.user.notifications.unread().count()}, status=status.HTTP_200_OK)


class MarkAsRead(views.APIView):

    def post(self, request, slug):
        try:
            instance = request.user.notifications.get(id=slug2id(slug))
        except Notification.DoesNotExist:
            return Response('Nie ma takiego powiadomienia!', status=status.HTTP_404_NOT_FOUND)
        if instance.unread:
            instance.mark_as_read()
            return Response('Oznaczono powiadomienie jako przeczytane', status=status.HTTP_200_OK)
        else:
            instance.mark_as_unread()
            return Response('Oznaczono powiadomienie jako nieprzeczytane', status=status.HTTP_200_OK)


class MarkAllAsRead(views.APIView):
    def post(self, request):
        request.user.notifications.mark_all_as_read()
        return Response('Oznaczono wszystkie powiadomienia jako przeczytane', status=status.HTTP_200_OK)


class Delete(views.APIView):
    def delete(self, request, slug):
        try:
            instance = request.user.notifications.get(id=slug2id(slug))
        except Notification.DoesNotExist:
            return Response('Nie ma takiego powiadomienia!', status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response('Pomyślnie usunięto powiadomienie!', status=status.HTTP_200_OK)

class DeleteAll(views.APIView):
    def delete(self, request):
        request.user.notifications.all().delete()
        return Response('Usunięto wszystkie twoje powiadomienia!', status=status.HTTP_200_OK)