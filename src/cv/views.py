import os
from drf_yasg import openapi
from django.http import HttpResponse, JsonResponse
from django.utils.datastructures import MultiValueDictKeyError
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from usamo import settings
from .models import CV
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas import ManualSchema
from cv.serializers import *
from rest_framework import status, generics, parsers, renderers
from rest_framework.response import Response
from rest_framework import views
from rest_framework.authtoken.models import Token


def index(request):
    return HttpResponse("Hello, world. You're at the CV generator.")


class GenerateView(views.APIView):
    serializer_class = CVSerializer

    @swagger_auto_schema(
        request_body=CVSerializer,
        responses={
            '201': 'CV successfully generated.',
            '400': "Bad Request"
        },
        operation_description="Create or update database object for CV generation.",
    )
    def post(self, request):
        request_data = request.data
        request_data['cv_id'] = request.user.id
        serializer = self.serializer_class(data=request_data)

        if serializer.is_valid():
            cv = serializer.create(serializer.validated_data)
            return Response('CV successfully generated.', status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_406_NOT_ACCEPTABLE)

    @swagger_auto_schema(
        operation_description='Generate pdf url based on existing CV data.',
        responses={
            '200': 'url',
            '404': 'CV not found'
    }
    )
    def get(self, request):
        if request.user.is_staff:
            cv_id = request.data['cv_id']
        else:
            cv_id = request.user.id
        try:
            cv = CV.objects.get(cv_id=cv_id)
        except CV.DoesNotExist:
            return Response('CV not found', status.HTTP_404_NOT_FOUND)

        return Response(cv.document.url, status.HTTP_200_OK)


    @swagger_auto_schema(
        operation_description="Deletes current user's cv from database if it exists",
        responses={
            '200': 'CV deleted successfully',
            '404': 'CV not found'
        }
    )
    def delete(self, request):
        cv_id = request.user.id
        try:
            CV.objects.filter(cv_id=cv_id).delete()
        except CV.DoesNotExist:
            return Response('CV not found', status.HTTP_404_NOT_FOUND)

        return Response('CV deleted successfully', status.HTTP_200_OK)


class DataView(views.APIView):
    @swagger_auto_schema(
        operation_description="Returns current user's CV data in json format",
        responses={
            '200': CVSerializer,
            '404': 'CV not found'
        }
    )
    def get(self, request):
        try:
            cv = CV.objects.get(cv_id=request.user.id)
        except CV.DoesNotExist:
            return Response('CV not found', status.HTTP_404_NOT_FOUND)
        serializer = CVSerializer(instance=cv)
        return JsonResponse(serializer.data)


class PictureView(views.APIView):
    @swagger_auto_schema(
        operation_description="Posts picture to be used in user's CV. Parameter 'cv_id' should not be posted here",

        manual_parameters=[
            openapi.Parameter(
                in_='header',
                name='Content-Type',
                type=openapi.TYPE_STRING,
                default='application/x-www-form-urlencoded'
            ),
            openapi.Parameter(
                name='picture',
                in_='form-data',
                type=openapi.TYPE_FILE
            )],
        responses={
            '201': 'Picture added successfully.',
            '404': 'CV not found.',
            '406': 'Make sure the form key is "picture".'
        }
    )
    def post(self, request):
        user = request.user
        user_id = user.id
        try:
            cv = CV.objects.get(cv_id=request.user.id)
        except CV.DoesNotExist:
            return Response('CV not found.', status.HTTP_404_NOT_FOUND)
        serializer = CVSerializer(instance=cv)
        data = serializer.data
        try:
            pict = request.FILES['picture']
            ext = pict.name.split('.')[-1]
            pict.name = create_unique_filename('cv_pics', ext)
            data['basic_info']['picture'] = pict
        except MultiValueDictKeyError:
            Response('Make sure the form key is "picture".', status.HTTP_406_NOT_ACCEPTABLE)
        serializer = CVSerializer(data=data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return Response('Picture added successfully.', status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_406_NOT_ACCEPTABLE)

    @swagger_auto_schema(
        operation_description="Returns user's picture url if uploaded",
        responses={
            200:'url',
            404:'CV/picture not found'
        }
    )
    def get(self, request):
        try:
            cv = CV.objects.get(cv_id=request.user.id)
        except CV.DoesNotExist:
            return Response('CV not found.', status.HTTP_404_NOT_FOUND)
        bi = BasicInfo.objects.get(cv=cv)
        if not bi.picture:
            return Response('Picture not found.', status.HTTP_404_NOT_FOUND)
        return Response(bi.picture.url, status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Deletes cv picture from the database",
        responses={
            200:'Picture deleted successfully.',
            404:'CV/picture not found.'
        }
    )
    def delete(self, request):
        try:
            cv = CV.objects.get(cv_id=request.user.id)
        except CV.DoesNotExist:
            return Response('CV not found.', status.HTTP_404_NOT_FOUND)
        bi = BasicInfo.objects.get(cv=cv)
        if not bi.picture:
            return Response('Picture not found.', status.HTTP_404_NOT_FOUND)
        bi.picture.delete(save=True)
        cv_serializer = CVSerializer(instance=cv)
        bi_serializer = BasicInfoSerializer(instance=bi)
        cv_serializer.data['basic_info'] = bi_serializer.data
        cv_serializer.create(cv_serializer.data)

        return Response('Picture deleted successfully.', status.HTTP_200_OK)

class UnverifiedCVList(generics.ListAPIView):
    """
    Returns a list of CVs whose owners want them to be
    verified and which haven't yet been verified.
    Requires admin privileges.
    """
    serializer_class = CVSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return CV.objects.filter(wants_verification=True, is_verified=False)


class AdminFeedback(generics.CreateAPIView):
    """
    Adds feedback from admin to an existing CV.
    Requires admin privileges.
    """
    permission_classes = [IsAdminUser]
    serializer_class = FeedbackSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UserFeedback(generics.RetrieveAPIView):
    """
    Returns current user's CV feedback from admin.
    """
    serializer_class = FeedbackSerializer

    def get_object(self):
        fb = get_object_or_404(Feedback.objects.filter(cv_id=self.request.user.id))
        return fb


class UserCVStatus(views.APIView):
    @swagger_auto_schema(
        operation_description="Returns current user's cv verification status",
        responses={
            200: 'is_verified: true/false',
            404: 'detail: not found'
        }
    )
    def get(self, request):
        cv = get_object_or_404(CV.objects.filter(cv_id=request.user.id))
        response = {"is_verified": cv.is_verified}
        return JsonResponse(response, safe=False)
