from django.shortcuts import render
from rest_framework import views, status, generics
from rest_framework.permissions import IsAuthenticated
from account.permissions import IsStaffMember
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.openapi import Parameter, IN_PATH
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from .serializers import *

# Create your views here.


class PhoneContactCreateView(views.APIView):
    permission_classes = [IsStaffMember]

    @swagger_auto_schema(
        request_body=PhoneContactSerializer,
        responses={
            201: 'Kontakt został pomyślnie utworzony',
            400: 'Błędy walidacji (np. brak jakiegoś pola)'
        }
    )
    def post(self, request):
        serializer = PhoneContactSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.create(serializer.validated_data)
            instance.save()
            return Response("Kontakt został pomyślnie dodany", status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class PhoneContactView(views.APIView):
    permission_classes = [IsStaffMember]

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('contact_id', IN_PATH, type='string($uuid)'),
        ],
        responses={
            200: 'Kontakt został pomyślnie usunięty',
            404: 'Nie znaleziono kontaktu o podanym id'
        }
    )
    def delete(self, request, contact_id):
        try:
            instance = PhoneContact.objects.get(pk=contact_id)
        except ObjectDoesNotExist:
            return Response("Nie znaleziono kontaktu o podanym id", status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response("Kontakt został pomyślnie usunięty", status.HTTP_200_OK)


@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        403: 'Nie masz uprawnień, by wykonać tę czynność.',
        404: 'Not found'
    },
    operation_description="Zwraca listę kontaków"
))
class PhoneContactListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PhoneContactSerializer

    def get_queryset(self):
        queryset = PhoneContact.objects.all()
        return queryset
