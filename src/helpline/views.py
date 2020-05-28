from django.shortcuts import render
from rest_framework import views, status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from account.permissions import IsStaffMember
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.openapi import Parameter, IN_PATH
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from .serializers import *
from job.views import ErrorResponse, MessageResponse, sample_message_response, sample_error_response
from rest_framework.filters import OrderingFilter
from blog.permissions import IsStaffBlogModerator


class PhoneContactCreateView(views.APIView):
    permission_classes = [IsStaffBlogModerator]

    @swagger_auto_schema(
        request_body=PhoneContactSerializer,
        responses={
            201: "id: 1 itd.",
            400: 'Błędy walidacji (np. brak jakiegoś pola)'
        }
    )
    def post(self, request):
        serializer = PhoneContactSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.create(serializer.validated_data)
            return Response({"id": instance.pk}, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class PhoneContactView(views.APIView):
    permission_classes = [IsStaffBlogModerator]

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('contact_id', IN_PATH, type='integer'),
        ],
        responses={
            200: sample_message_response('Kontakt został pomyślnie usunięty'),
            404: sample_message_response("Nie znaleziono kontaktu o podanym id")
        }
    )
    def delete(self, request, contact_id):
        try:
            instance = PhoneContact.objects.get(pk=contact_id)
        except ObjectDoesNotExist:
            return ErrorResponse("Nie znaleziono kontaktu o podanym id", status.HTTP_404_NOT_FOUND)
        instance.delete()
        return MessageResponse("Kontakt został pomyślnie usunięty")


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Zwraca listę telefonów"
))
class PhoneContactListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PhoneContactSerializer
    filter_backends = [OrderingFilter]
    ordering = ['pk']

    def get_queryset(self):
        queryset = PhoneContact.objects.all()
        return queryset
