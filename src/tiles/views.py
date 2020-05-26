from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from drf_yasg.openapi import Parameter, IN_PATH
from rest_framework import generics
from .serializers import *
from account.permissions import IsStaffMember
from rest_framework import views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from job.views import ErrorResponse, MessageResponse, sample_message_response, sample_error_response
from rest_framework.filters import OrderingFilter
from django.utils.decorators import method_decorator
from drf_yasg import openapi

# Create your views here.


class TileCreateView(views.APIView):
    permission_classes = [IsStaffMember]

    @swagger_auto_schema(
        request_body=TileSerializer,
        responses={
            201: "id: 1 itd.",
            400: 'Błędy walidacji (np. brak jakiegoś pola)'
        }
    )
    def post(self, request):
        serializer = TileSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.create(serializer.validated_data)
            return Response({"id": instance.pk}, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class TileView(views.APIView):
    permission_classes = [IsStaffMember]

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('tile_id', IN_PATH, type='integer')
        ],
        responses={
            200: '"message": "Kafelek o podanym id został zaktualizowany"',
            403: 'Forbidden - no permissions',
            404: '"error": "Nie znaleziono kafelka o podanym id"'
        }
    )
    def put(self, request, tile_id):
        try:
            instance = Tile.objects.get(id=tile_id)
            serializer = TileSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.update(instance, serializer.validated_data)
                response_data = {"message": "Kafelek o podanym id został zaktualizowany"}
                return Response(response_data, status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return ErrorResponse("Nie znaleziono kafelka o podanym id", status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('tile_id', IN_PATH, type='integer'),
        ],
        responses={
            200: sample_message_response('Kafelek został pomyślnie usunięty'),
            404: sample_message_response("Nie znaleziono kafelka o podanym id")
        }
    )
    def delete(self, request, tile_id):
        try:
            instance = Tile.objects.get(pk=tile_id)
        except ObjectDoesNotExist:
            return ErrorResponse("Nie znaleziono kafelka o podanym id", status.HTTP_404_NOT_FOUND)
        instance.delete()
        return MessageResponse("Kafelek został pomyślnie usunięty")


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Zwraca listę kafelków"
))
class TileListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = TileSerializer
    filter_backends = [OrderingFilter]
    ordering = ['pk']

    def get_queryset(self):
        queryset = Tile.objects.all()
        return queryset


class TilePhotoView(views.APIView):
    permissions_classes = [IsStaffMember]

    @swagger_auto_schema(
        operation_description="Posts photo to be used in Tile.",

        manual_parameters=[
            openapi.Parameter(
                in_='header',
                name='Content-Type',
                type=openapi.TYPE_STRING,
                default='application/x-www-form-urlencoded'
            ),
            openapi.Parameter(
                name='photo',
                in_='form-data',
                type=openapi.TYPE_FILE
            ),
            openapi.Parameter('tile_id', openapi.IN_PATH, type='integer',
                              description='Integer będący id danego kafelka')
        ],
        responses={
            '200': 'Zdjęcie dodano pomyślnie',
            '400': 'Upewnij się, że form key to "photo" / Błędy walidacji',
            '403': "Nie masz uprawnień do wykonania tej czynności",
            '404': 'Nie znaleziono Kafelka. Upewnij się, że uwzględniono tile_id w url-u'
        }
    )
    def post(self, request, tile_id):
        try:
            tile = Tile.objects.get(pk=tile_id)
        except Tile.DoesNotExist:
            return ErrorResponse("Nie znaleziono kafelka o podanym id", status.HTTP_404_NOT_FOUND)

        try:
            tile.photo = request.FILES['photo']
        except MultiValueDictKeyError:
            return ErrorResponse('Nie znaleziono pliku. Upewnij się, że został on załączony pod kluczem photo'
                                 , status.HTTP_400_BAD_REQUEST)

        tile.save()
        response_data = {"id": tile.id, "attachment_url": tile.photo.url}
        return Response(response_data, status.HTTP_200_OK)

