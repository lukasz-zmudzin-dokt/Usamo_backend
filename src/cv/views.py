from django.http import JsonResponse
from drf_yasg import openapi
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics
from rest_framework import views
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from account.permissions import IsStandardUser
from .models import *
from .serializers import *
from .permissions import *
from job.views import sample_message_response


class CreateCVView(views.APIView):

    permission_classes = [IsStandardUser]
    serializer_class = CVSerializer

    @swagger_auto_schema(
        request_body=CVSerializer,
        responses={
            '201': 'CV successfully generated.',
            '400': 'Serializer errors',
            '403': "User type is not standard"
        },
        operation_description="Create or update database object for CV generation.",
    )
    def post(self, request):
        request_data = request.data
        def_account = DefaultAccount.objects.get(user=request.user)
        request_data['cv_user'] = def_account.id
        serializer = self.serializer_class(data=request_data)

        if serializer.is_valid():
            cv = serializer.create(serializer.validated_data)
            response = {"cv_id" : cv.pk}
            return Response(response, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class CVView(views.APIView):

    permissions_classes = [IsCVOwner | IsStaffResponsibleForCVs]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)', 
                description='A UUID string identifying this cv')
        ],
        responses={
            '200': sample_message_response("/media/cv_docs/2020/04/03/file_name.pdf"),
            '403': 'User has no permission to perfonm this action.',
            '404': "CV not found. Make sure cv_id was specified in the url."
        },
        operation_description='Generate pdf url based on existing CV data.'
    )
    def get(self, request, **kwargs):
        cv_id = kwargs.get('cv_id', None)
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv) \
                    or not IsStaffResponsibleForCVs().has_object_permission(request, self, cv):
                return Response("User has no permission to perfonm this action.", status.HTTP_403_FORBIDDEN)
        except CV.DoesNotExist:
            return Response("CV not found. Make sure cv_id was specified in the url.", status.HTTP_404_NOT_FOUND)

        return Response(cv.document.url, status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Deletes cv from database if it exists",
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)', 
                description='A UUID string identifying this cv')
        ],
        responses={
            '200': 'CV deleted successfully.',
            '403': 'User has no permission to perfonm this action.',
            '404': "CV not found. Make sure cv_id was specified in the url."
        }
    )
    def delete(self, request, **kwargs):
        cv_id = kwargs.get('cv_id', None)
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv) \
                    or not IsStaffResponsibleForCVs().has_object_permission(request, self, cv):
                return Response("User has no permission to perfonm this action.", status.HTTP_403_FORBIDDEN)
            cv.delete()
        except CV.DoesNotExist:
            return Response("CV not found. Make sure cv_id was specified in the url.", status.HTTP_404_NOT_FOUND)

        return Response('CV deleted successfully.', status.HTTP_200_OK)


class CVDataView(views.APIView):

    permissions_classes = [IsCVOwner | IsStaffResponsibleForCVs]

    @swagger_auto_schema(
        operation_description="Returns CV data in json format",
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)', 
                description='A UUID string identifying this cv') 
        ],
        responses={
            '200': CVSerializer,
            '403': "User has no permission to perfonm this action.",
            '404': "CV not found."
        }
    )
    def get(self, request, **kwargs):
        cv_id = kwargs.get('cv_id', None)
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv) \
                    or not IsStaffResponsibleForCVs().has_object_permission(request, self, cv):
                return Response("User has no permission to perfonm this action.", status.HTTP_403_FORBIDDEN)
        except CV.DoesNotExist:
            return Response("CV not found.", status.HTTP_404_NOT_FOUND)
        serializer = CVSerializer(instance=cv)
        return Response(serializer.data, status.HTTP_200_OK)


class CVPictureView(views.APIView):

    permissions_classes = [IsCVOwner | IsStaffResponsibleForCVs]

    @swagger_auto_schema(
        operation_description="Posts picture to be used in CV.",

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
            ),
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)', 
                description='A UUID string identifying this cv')
        ],
        responses={
            '201': 'Picture added successfully.',
            '400': 'Make sure the form key is "picture". / serializer errors ',
            '403': "User has no permission to perfonm this action.",
            '404': 'CV not found.'
        }
    )
    def post(self, request, **kwargs):
        cv_id = kwargs.get('cv_id', None)
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv):
                return Response("User has no permission to perfonm this action.", status.HTTP_403_FORBIDDEN)
        
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
            Response('Make sure the form key is "picture".', status.HTTP_400_BAD_REQUEST)
        serializer = CVSerializer(data=data)
        if serializer.is_valid():
            serializer.update(cv, serializer.validated_data)
            return Response('Picture added successfully.', status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        operation_description="Returns picture url if it was uploaded",
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)', 
                description='A UUID string identifying this cv')
        ],
        responses={
            '200': sample_message_response("/media/cv_pics/2020/04/03/file_name.png"),
            '403': "User has no permission to perfonm this action.",
            '404': 'CV/picture not found'
        }
    )
    def get(self, request, **kwargs):
        cv_id = kwargs.get('cv_id', None)
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv) \
                    or not IsStaffResponsibleForCVs().has_object_permission(request, self, cv):
                return Response("User has no permission to perfonm this action.", status.HTTP_403_FORBIDDEN)
        except CV.DoesNotExist:
            return Response('CV not found.', status.HTTP_404_NOT_FOUND)
        bi = BasicInfo.objects.get(cv=cv)
        if not bi.picture:
            return Response('Picture not found.', status.HTTP_404_NOT_FOUND)
        return Response(bi.picture.url, status.HTTP_200_OK)


    @swagger_auto_schema(
        operation_description="Deletes cv picture from the database",
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)', 
                description='A UUID string identifying this cv')
        ],
        responses={
            '200': 'Picture deleted successfully.',
            '403': "User has no permission to perfonm this action.",
            '404': 'CV/picture not found.'
        }
    )
    def delete(self, request, **kwargs):
        cv_id = kwargs.get('cv_id', None)
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv) \
                    or not IsStaffResponsibleForCVs().has_object_permission(request, self, cv):
                return Response("User has no permission to perfonm this action.", status.HTTP_403_FORBIDDEN)
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

@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        '200': CVSerializer(many=True),
        '404': "Not found",
    },
    operation_description="Returns unverified cv list for admin"
))
class AdminUnverifiedCVList(generics.ListAPIView):
    serializer_class = CVSerializer
    permission_classes = [IsStaffResponsibleForCVs]

    def get_queryset(self):
        return CV.objects.filter(is_verified=False)


class AdminFeedback(views.APIView):
    """
    Adds feedback from admin to an existing CV.
    Requires admin privileges.
    """
    permission_classes = [IsStaffResponsibleForCVs]
    serializer_class = FeedbackSerializer

    @swagger_auto_schema(
        request_body=FeedbackSerializer,
        responses={
            '201': 'Feedback successfully created.',
            '400': 'Serializer errors'
        },
        operation_description="Lets admin create feedback for a cv.",
    )
    def post(self, request):
        request_data = request.data
        serializer = self.serializer_class(data=request_data)
        try:
            cv = CV.objects.get(cv_id=request_data['cv_id'])
        except CV.DoesNotExist:
            return Response('CV with the given id was not found.', status.HTTP_404_NOT_FOUND)

        if serializer.is_valid():
            feedback = serializer.create(serializer.validated_data)
            return Response('Feedback successfully created.', status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        '200': FeedbackSerializer,
        '403': "User has no permission to perfonm this action.",
        '404': "Not found"
    },
    manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string')
        ],
    operation_description="Returns feedback for users cv"
))
class CVFeedback(views.APIView):
    
    permission_classes = [IsCVOwner | IsStaffResponsibleForCVs]

    def get(self, request, **kwargs):
        cv_id = kwargs.get('cv_id', None)
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv) \
                    or not IsStaffResponsibleForCVs().has_object_permission(request, self, cv):
                return Response("User has no permission to perfonm this action.", status.HTTP_403_FORBIDDEN)
        except CV.DoesNotExist:
            return Response('CV not found.', status.HTTP_404_NOT_FOUND)
        
        try:
            fb = Feedback.objects.get(cv_id=cv_id)
        except Feedback.DoesNotExist:
            return Response('Feedback not found.', status.HTTP_404_NOT_FOUND)
    
        serializer = FeedbackSerializer(instance=fb)
        return Response(serializer.data, status.HTTP_200_OK)


class AdminCVVerificationView(views.APIView):
    permission_classes = [IsStaffResponsibleForCVs]

    @swagger_auto_schema(
        responses={
            '200': 'CV was successfully verified.',
            '400': 'CV id was not specified.',
            '404': 'CV with the given id was not found.'
        },
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)', 
                description='A UUID string identifying cv.')
        ],
        operation_description="Sets cv's status to verified.",
    )
    def post(self, request, cv_id):
        if cv_id is not None:
            try:
                cv = CV.objects.get(cv_id=cv_id)
            except CV.DoesNotExist:
                return Response('CV with the given id was not found.', status.HTTP_404_NOT_FOUND)
            cv.is_verified = True
            cv.save()
            return Response('CV successfully verified.', status.HTTP_200_OK)

        return Response('CV id was not specified.', status.HTTP_400_BAD_REQUEST)


class CVStatus(views.APIView):

    permission_classes = [IsCVOwner | IsStaffResponsibleForCVs]

    @swagger_auto_schema(
        operation_description="Returns cv verification status",
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)', 
                description='A UUID string identifying this cv')
        ],
        responses={
            '200': 'is_verified: true/false',
            '403': 'User has no permission to perfonm this action.',
            '404': 'Not found'
        }
    )
    def get(self, request, **kwargs):
        cv_id = kwargs.get('cv_id', None)
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv) \
                    or not IsStaffResponsibleForCVs().has_object_permission(request, self, cv):
                return Response("User has no permission to perfonm this action.", status.HTTP_403_FORBIDDEN)
        except CV.DoesNotExist:
            return Response('CV not found.', status.HTTP_404_NOT_FOUND)

        return Response({"is_verified": cv.is_verified}, status.HTTP_200_OK)


@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        '200': CVSerializer(many=True),
        '404': "Not found",
    },
    operation_description="Returns all CVs list for admin"
))
class AdminCVListView(generics.ListAPIView):
    queryset = CV.objects.all()
    serializer_class = CVSerializer
    permission_classes = [IsStaffResponsibleForCVs]


@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        '200': CVSerializer(many=True),
        '404': "Not found",
    },
    operation_description="Returns users CV list"
))
class UserCVListView(generics.ListAPIView):
    serializer_class = CVSerializer
    permission_classes = [IsStandardUser]

    def get_queryset(self):
        user = self.request.user
        def_account = get_object_or_404(
            DefaultAccount.objects.filter(user=user))
        return CV.objects.filter(cv_user=def_account)


class UserCVNameView(views.APIView):
    @swagger_auto_schema(
        operation_description="Changes the name of a CV",
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)',
                              description='A UUID string identifying this cv')
        ],
        request_body = openapi.Schema(type='object', properties= {
            'name': openapi.Schema(type='string')}),

        responses={
            200: 'CV name changed to: new_name',
            403: 'User has no permission to perfonm this action.',
            404: 'CV with the given id  does not exist',
            400: 'New name was not specified'
        }
    )
    def put(self, request, cv_id):
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv) \
                    or not IsStaffResponsibleForCVs().has_object_permission(request, self, cv):
                return Response("User has no permission to perfonm this action.", status.HTTP_403_FORBIDDEN)

        except CV.DoesNotExist:
            return Response('CV with the given id  does not exist', status=status.HTTP_404_NOT_FOUND)

        try:
            instance.name = request.data['name']
            instance.save()
            return Response(f'CV name changed to: {request.data["name"]}', status=status.HTTP_200_OK)
        except KeyError:
            return Response('New name was not specified', status=status.HTTP_400_BAD_REQUEST)



