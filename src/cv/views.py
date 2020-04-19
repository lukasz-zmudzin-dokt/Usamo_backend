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

from cv.models import CV
from cv.serializers import *
from job.views import sample_message_response


class CreateCVView(views.APIView):
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

        try:
            def_account = DefaultAccount.objects.get(user=request.user)
        except DefaultAccount.DoesNotExist:
            return Response('User type is not standard', status.HTTP_403_FORBIDDEN)

        request_data['cv_user'] = def_account.id
        serializer = self.serializer_class(data=request_data)

        if serializer.is_valid():
            cv = serializer.create(serializer.validated_data)
            response = {"cv_id" : cv.pk}
            return Response(response, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class CVView(views.APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)', 
                description='A UUID string identifying this cv')
        ],
        responses={
            '200': sample_message_response("/media/cv_docs/2020/04/03/file_name.pdf"),
            '404': "CV not found. Make sure cv_id was specified in the url."
        },
        operation_description='Generate pdf url based on existing CV data.'
    )
    def get(self, request, **kwargs):
        cv_id = kwargs.get('cv_id', None)
        try:
            cv = CV.objects.get(cv_id=cv_id)
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
            '404': "CV not found. Make sure cv_id was specified in the url."
        }
    )
    def delete(self, request, **kwargs):
        cv_id = kwargs.get('cv_id', None)
        try:
            cv = CV.objects.get(cv_id=cv_id)
            cv.delete()
        except CV.DoesNotExist:
            return Response("CV not found. Make sure cv_id was specified in the url.", status.HTTP_404_NOT_FOUND)

        return Response('CV deleted successfully.', status.HTTP_200_OK)


class CVDataView(views.APIView):
    @swagger_auto_schema(
        operation_description="Returns CV data in json format",
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)', 
                description='A UUID string identifying this cv') 
        ],
        responses={
            '200': CVSerializer,
            '404': "CV not found."
        }
    )
    def get(self, request, **kwargs):
        cv_id = kwargs.get('cv_id', None)
        try:
            cv = CV.objects.get(cv_id=cv_id)
        except CV.DoesNotExist:
            return Response("CV not found.", status.HTTP_404_NOT_FOUND)
        serializer = CVSerializer(instance=cv)
        return Response(serializer.data, status.HTTP_200_OK)


class CVPictureView(views.APIView):
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
            '404': 'CV not found.'
        }
    )
    def post(self, request, **kwargs):
        cv_id = kwargs.get('cv_id', None)
        try:
            cv = CV.objects.get(cv_id=cv_id)
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
            200: sample_message_response("/media/cv_pics/2020/04/03/file_name.png"),
            404: 'CV/picture not found'
        }
    )
    def get(self, request, **kwargs):
        cv_id = kwargs.get('cv_id', None)
        try:
            cv = CV.objects.get(cv_id=cv_id)
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
            200: 'Picture deleted successfully.',
            404: 'CV/picture not found.'
        }
    )
    def delete(self, request, **kwargs):
        cv_id = kwargs.get('cv_id', None)
        try:
            cv = CV.objects.get(cv_id=cv_id)
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
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return CV.objects.filter(wants_verification=True, is_verified=False)


class AdminFeedback(views.APIView):
    """
    Adds feedback from admin to an existing CV.
    Requires admin privileges.
    """
    permission_classes = [IsAdminUser]
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
        '404': "Not found",
    },
    manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string')
        ],
    operation_description="Returns feedback for users cv"
))
class CVFeedback(generics.RetrieveAPIView):
    
    serializer_class = FeedbackSerializer

    def get_object(self):
        fb = get_object_or_404(
            Feedback.objects.filter(cv_id=self.kwargs['cv_id']))
        return fb


class AdminCVVerificationView(views.APIView):
    permission_classes = [IsAdminUser]

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
    @swagger_auto_schema(
        operation_description="Returns cv verification status",
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)', 
                description='A UUID string identifying this cv')
        ],
        responses={
            200: 'is_verified: true/false',
            404: 'detail: not found'
        }
    )
    def get(self, request, *args, **kwargs):
        cv = get_object_or_404(CV.objects.filter(cv_id=kwargs['cv_id']))
        response = {"is_verified": cv.is_verified}
        return JsonResponse(response, safe=False)


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
    permission_classes = [IsAdminUser]


@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        '200': CVSerializer(many=True),
        '404': "Not found",
    },
    operation_description="Returns users CV list"
))
class UserCVListView(generics.ListAPIView):
    serializer_class = CVSerializer
    permission_classes = [IsAuthenticated]

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
                              description='A UUID string identifying this cv'),
            openapi.Parameter('name', openapi.IN_BODY, type='string',
                              description='New CV name')
        ],
        responses={
            200: 'Nazwa CV zmieniona na: nowanazwa',
            403: 'Podane CV nie należy do danego użytkownika',
            404: 'Podane CV nie istnieje',
            406: 'Nie podano nowej nazwy CV'
        }
    )
    def put(self, request, cv_id):
        try:
            instance = CV.objects.get(cv_id=cv_id)
        except CV.DoesNotExist:
            return Response('Podane CV nie istnieje', status=status.HTTP_404_NOT_FOUND)

        if not instance.cv_user.user == request.user:
            return Response('Podane CV nie należy do danego użytkownika', status=status.HTTP_403_FORBIDDEN)

        try:
            instance.name = request.data['name']
            instance.save()
            return Response(f'Nazwa CV zmieniona na: {request.data["name"]}', status=status.HTTP_200_OK)
        except KeyError:
            return Response('Nie podano nowej nazwy CV', status=status.HTTP_400_BAD_REQUEST)



