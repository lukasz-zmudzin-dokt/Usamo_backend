from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics
from rest_framework import views
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from account.account_type import StaffGroupType
from account.models import StaffAccount
from account.permissions import IsStandardUser, IsCVOwner, IsStaffResponsibleForCVs, IsAGuest

from .filters import CvOrderingFilter, CVListFilter, DjangoFilterDescriptionInspector
from .models import *
from .serializers import *
from .templates.templates import *
from job.views import sample_message_response, ErrorResponse, MessageResponse
import base64
from notifications.signals import notify


class CVPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CreateCVView(views.APIView):
    permission_classes = [IsStandardUser]
    serializer_class = CVSerializer

    @swagger_auto_schema(
        request_body=CVSerializer,
        responses={
            '201': '"cv_id" : id',
            '400': 'Błędy walidacji (np. brak jakiegoś pola)',
            '403': "You do not have permission to perform this action. \
                    / Użytkownik posiada już 5 CV!"
        },
        operation_description="Tworzenie obiektu CV dla danego użytkownika",
    )
    def post(self, request):
        request_data = request.data
        def_account = DefaultAccount.objects.get(user=request.user)
        users_cvs = CV.objects.filter(cv_user=def_account)

        if not users_cvs.count() < 5:
            return ErrorResponse("Użytkownik posiada już 5 CV!", status.HTTP_403_FORBIDDEN)

        request_data['cv_user'] = def_account.id
        serializer = self.serializer_class(data=request_data)

        if serializer.is_valid():
            cv = serializer.create(serializer.validated_data)
            response = {"cv_id": cv.pk}
            notify.send(request.user, recipient=Account.objects.filter(groups__name__contains='staff_cv'),
                        verb=f'Użytkownik {def_account.user.username} utworzył_a nowe CV',
                        app='cv/generator/',
                        object_id=cv.cv_id
                        )
            return Response(response, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class CVView(views.APIView):
    permissions_classes = [IsCVOwner | IsStaffResponsibleForCVs]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)',
                              description='String UUID będący id danego CV')
        ],
        responses={
            '200': sample_message_response("/media/cv_docs/2020/04/03/file_name.pdf"),
            '403': 'Nie masz uprawnień do wykonania tej czynności',
            '404': "Nie znaleziono CV. Upewnij się, że uwzględniono cv_id w url-u"
        },
        operation_description='Zwraca url-a do pdf zawierającego CV na podstawie zapisanych wcześniej danych'
    )
    def get(self, request, cv_id):
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv) \
                    and not IsStaffResponsibleForCVs().has_object_permission(request, self, cv):
                return ErrorResponse("Nie masz uprawnień do wykonania tej czynności", status.HTTP_403_FORBIDDEN)
        except CV.DoesNotExist:
            return ErrorResponse("Nie znaleziono CV. Upewnij się, że uwzględniono cv_id w url-u", status.HTTP_404_NOT_FOUND)

        return Response({'url': cv.document.url}, status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Usuwa CV z bazy danych jeśli ono istnieje",
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)',
                              description='String UUID będący id danego CV')
        ],
        responses={
            '200': 'CV usunięto pomyślnie',
            '403': 'Nie masz uprawnień do wykonania tej czynności.',
            '404': "Nie znaleziono CV. Upewnij się, że uwzględniono cv_id w url-u"
        }
    )
    def delete(self, request, cv_id):
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv) \
                    and not IsStaffResponsibleForCVs().has_object_permission(request, self, cv):
                return ErrorResponse("Nie masz uprawnień do wykonania tej czynności", status.HTTP_403_FORBIDDEN)
            cv.delete()
        except CV.DoesNotExist:
            return ErrorResponse("Nie znaleziono CV. Upewnij się, że uwzględniono cv_id w url-u", status.HTTP_404_NOT_FOUND)

        return MessageResponse('CV usunięto pomyślnie')


class CVDataView(views.APIView):
    permissions_classes = [IsCVOwner | IsStaffResponsibleForCVs]

    @swagger_auto_schema(
        operation_description="Zwraca dane do CV w formacie json",
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)',
                              description='String UUID będący id danego CV')
        ],
        responses={
            '200': CVSerializer,
            '403': "Nie masz uprawnień do wykonania tej czynności",
            '404': "Nie znaleziono CV. Upewnij się, że uwzględniono cv_id w url-u"
        }
    )
    def get(self, request, cv_id):
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv) \
                    and not IsStaffResponsibleForCVs().has_object_permission(request, self, cv):
                return ErrorResponse("Nie masz uprawnień do wykonania tej czynności", status.HTTP_403_FORBIDDEN)
        except CV.DoesNotExist:
            return ErrorResponse("Nie znaleziono CV. Upewnij się, że uwzględniono cv_id w url-u", status.HTTP_404_NOT_FOUND)
        serializer = CVSerializer(instance=cv)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Lets user edit his CV",
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)',
                description='A UUID string identifying this cv')
        ],
        responses={
            '200': 'message: CV edytowane pomyślnie',
            '400': 'Błędy walidacji (np. brak jakiegoś pola)',
            '403': "Nie masz uprawnień do wykonania tej czynności",
            '404': "Nie znaleziono cv"
        }
    )
    def put(self, request, cv_id):
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv):
                return ErrorResponse("Nie masz uprawnień do wykonania tej czynności", status.HTTP_403_FORBIDDEN)
        except CV.DoesNotExist:
            return ErrorResponse("Nie znaleziono cv", status.HTTP_404_NOT_FOUND)
        serializer = CVSerializer(data=request.data)

        delete_previous_cv_file(cv)

        if serializer.is_valid():
            serializer.update(cv, serializer.validated_data)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        response = {'message': 'CV edytowane pomyślnie'}
        return Response(response, status.HTTP_200_OK)


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
                              description='String UUID będący id danego CV')
        ],
        responses={
            '201': 'Zdjęcie dodano pomyślnie',
            '400': 'Upewnij się, że form key to "picture" / Błędy walidacji',
            '403': "Nie masz uprawnień do wykonania tej czynności",
            '404': 'Nie znaleziono CV. Upewnij się, że uwzględniono cv_id w url-u'
        }
    )
    def post(self, request, cv_id):
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv):
                return ErrorResponse("Nie masz uprawnień do wykonania tej czynności", status.HTTP_403_FORBIDDEN)

        except CV.DoesNotExist:
            return ErrorResponse('Nie znaleziono CV. Upewnij się, że uwzględniono cv_id w url-u', status.HTTP_404_NOT_FOUND)

        serializer = CVSerializer(instance=cv)
        data = serializer.data
        try:
            pict = request.FILES['picture']
            ext = pict.name.split('.')[-1]
            pict.name = create_unique_filename('cv_pics', ext)
            data['basic_info']['picture'] = pict
            cv.has_picture = True
            cv.save()
        except MultiValueDictKeyError:
            ErrorResponse('Upewnij się, że form key to "picture"', status.HTTP_400_BAD_REQUEST)
        serializer = CVSerializer(data=data)

        delete_previous_cv_file(cv)
        delete_previous_picture(cv.basic_info)

        if serializer.is_valid():
            serializer.update(cv, serializer.validated_data)
            return MessageResponse('Zdjęcie dodano pomyślnie')
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Zwraca obrazek w base64",
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)',
                              description='String UUID będący id danego CV')
        ],
        responses={
            '200': "file: base 64",
            '403': "Nie masz uprawnień do wykonania tej czynności",
            '404': 'Nie znaleziono CV/zdjęcia'
        }
    )
    def get(self, request, cv_id):
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv) \
                    and not IsStaffResponsibleForCVs().has_object_permission(request, self, cv):
                return ErrorResponse("Nie masz uprawnień do wykonania tej czynności", status.HTTP_403_FORBIDDEN)
        except CV.DoesNotExist:
            return ErrorResponse('Nie znaleziono CV', status.HTTP_404_NOT_FOUND)
        bi = BasicInfo.objects.get(cv=cv)
        if not bi.picture:
            return ErrorResponse('Nie znaleziono zdjęcia', status.HTTP_404_NOT_FOUND)

        encoded_string = base64.b64encode(bi.picture.read())

        response_data = {'file': encoded_string}

        return Response(response_data, status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Usuwa CV z bazy",
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)',
                              description='String UUID będący id danego CV')
        ],
        responses={
            '200': 'Zdjęcie usunięto pomyślnie',
            '403': "Nie masz uprawnień do wykonania tej czynności",
            '404': 'Nie znaleziono CV/zdjęcia'
        }
    )
    def delete(self, request, cv_id):
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv):
                return ErrorResponse("Nie masz uprawnień do wykonania tej czynności", status.HTTP_403_FORBIDDEN)
        except CV.DoesNotExist:
            return ErrorResponse('Nie znaleziono CV', status.HTTP_404_NOT_FOUND)
        bi = BasicInfo.objects.get(cv=cv)
        if not bi.picture:
            return ErrorResponse('Nie znaleziono zdjęcia', status.HTTP_404_NOT_FOUND)
        bi.picture.delete(save=True)
        cv.has_picture = False
        cv.save()
        cv_serializer = CVSerializer(instance=cv)

        delete_previous_picture(bi)
        delete_previous_cv_file(cv)
        cv_serializer.update(cv, cv_serializer.data)

        return MessageResponse('Zdjęcie usunięto pomyślnie')


@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[DjangoFilterDescriptionInspector],
    responses={
        '403': "User has no permission to perform this action.",
        '404': "Not found"
    },
    operation_description="Zwraca listę niezweryfikowanych CV dla admina"
))
class AdminUnverifiedCVList(generics.ListAPIView):
    serializer_class = CVSerializer
    permission_classes = [IsStaffResponsibleForCVs]
    pagination_class = CVPagination
    filter_backends = (DjangoFilterBackend, CvOrderingFilter,)
    filterset_class = CVListFilter
    ordering_fields = ['first_name', 'last_name', 'email', 'languages_count', 'date_created', 'has_picture',
                       'was_reviewed']
    ordering = ['-date_created']

    def get_queryset(self):
        return CV.objects\
            .select_related('cv_user') \
            .select_related('basic_info') \
            .prefetch_related('schools') \
            .prefetch_related('experiences') \
            .prefetch_related('skills') \
            .prefetch_related('languages') \
            .filter(is_verified=False)


class AdminFeedback(views.APIView):
    permission_classes = [IsStaffResponsibleForCVs]
    serializer_class = FeedbackSerializer

    @swagger_auto_schema(
        request_body=FeedbackSerializer,
        responses={
            '201': 'Feedback stworzono pomyślnie',
            '400': 'Błędy walidacji (np. brak jakiegoś pola)',
            '403': "User has no permission to perform this action.",
            '404': 'Nie znaleziono CV o podanym id'
        },
        operation_description="Tworzenie feedbacku do danego CV przez admina",
    )
    def post(self, request):
        request_data = request.data
        serializer = self.serializer_class(data=request_data)
        try:
            cv = CV.objects.get(cv_id=request_data['cv_id'])
        except CV.DoesNotExist:
            return ErrorResponse('Nie znaleziono CV o podanym id', status.HTTP_404_NOT_FOUND)

        if serializer.is_valid():
            feedback = serializer.create(serializer.validated_data)
            notify.send(request.user, recipient=cv.cv_user.user,
                        verb=f'Osoba z fundacji skomentowała twoje CV: {cv.name}',
                        app='cv/feedback/',
                        object_id=cv.cv_id
                        )
            return MessageResponse('Feedback stworzono pomyślnie')
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        '200': FeedbackSerializer,
        '403': "Nie masz uprawnień do wykonania tej czynności",
        '404': "Nie znaleziono CV/feedbacku"
    },
    manual_parameters=[
        openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)',
                          description='String UUID będący id danego CV')
    ],
    operation_description="Zwraca feedback do danego cv"
))
class CVFeedback(views.APIView):
    permission_classes = [IsCVOwner | IsStaffResponsibleForCVs]

    def get(self, request, cv_id):
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv) \
                    and not IsStaffResponsibleForCVs().has_object_permission(request, self, cv):
                return ErrorResponse("Nie masz uprawnień do wykonania tej czynności", status.HTTP_403_FORBIDDEN)
        except CV.DoesNotExist:
            return ErrorResponse('Nie znaleziono CV', status.HTTP_404_NOT_FOUND)

        try:
            fb = Feedback.objects.get(cv_id=cv_id)
        except Feedback.DoesNotExist:
            return ErrorResponse('Nie znaleziono feedbacku', status.HTTP_404_NOT_FOUND)

        serializer = FeedbackSerializer(instance=fb)
        return Response(serializer.data, status.HTTP_200_OK)


class AdminCVVerificationView(views.APIView):
    permission_classes = [IsStaffResponsibleForCVs]

    @swagger_auto_schema(
        responses={
            '200': 'CV zweryfikowano pomyślnie',
            '400': 'Nie podano cv_id',
            '403': "User has no permission to perform this action.",
            '404': 'Nie znaleziono CV o podanym id'
        },
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)',
                              description='String UUID będący id danego CV')
        ],
        operation_description="Zmienia status CV na zweryfikowane",
    )
    def post(self, request, cv_id):
        if cv_id is not None:
            try:
                cv = CV.objects.get(cv_id=cv_id)
            except CV.DoesNotExist:
                return ErrorResponse('Nie znaleziono CV o podanym id', status.HTTP_404_NOT_FOUND)
            cv.is_verified = True
            cv.save()
            notify.send(request.user, recipient=cv.cv_user.user,
                        verb=f'Osoba z fundacji zatwierdziła twoje CV: {cv.name}',
                        app='cv/generator/',
                        object_id=cv.cv_id
                        )
            return MessageResponse('CV zweryfikowano pomyślnie')
        return ErrorResponse('Nie podano cv_id', status.HTTP_400_BAD_REQUEST)


class CVStatus(views.APIView):
    permission_classes = [IsCVOwner | IsStaffResponsibleForCVs]

    @swagger_auto_schema(
        operation_description="Zwraca status weryfikacji danego CV",
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)',
                              description='A UUID string identifying this cv')
        ],
        responses={
            '200': 'is_verified: true/false',
            '403': 'Nie masz uprawnień do wykonania tej czynności',
            '404': 'Nie znaleziono CV o podanym id'
        }
    )
    def get(self, request, cv_id):
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv) \
                    and not IsStaffResponsibleForCVs().has_object_permission(request, self, cv):
                return ErrorResponse("Nie masz uprawnień do wykonania tej czynności", status.HTTP_403_FORBIDDEN)
        except CV.DoesNotExist:
            return ErrorResponse('Nie znaleziono CV o podanym id', status.HTTP_404_NOT_FOUND)

        return Response({"is_verified": cv.is_verified}, status.HTTP_200_OK)


@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[DjangoFilterDescriptionInspector],
    responses={
        '403': "Nie masz uprawnień, by wykonać tę czynność.",
        '404': "Not found",
    },
    operation_description="Zwraca listę wszystkich CV dla admina"
))
class AdminCVListView(generics.ListAPIView):
    serializer_class = CVSerializer
    permission_classes = [IsStaffResponsibleForCVs]
    pagination_class = CVPagination
    filter_backends = (DjangoFilterBackend, CvOrderingFilter,)
    filterset_class = CVListFilter
    ordering_fields = ['first_name', 'last_name', 'email', 'languages_count', 'date_created', 'has_picture',
                       'was_reviewed', 'is_verified']
    ordering = ['-date_created']

    def get_queryset(self):
        return CV.objects\
            .select_related('cv_user') \
            .select_related('basic_info') \
            .prefetch_related('schools') \
            .prefetch_related('experiences') \
            .prefetch_related('skills') \
            .prefetch_related('languages') \
            .all()

@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[DjangoFilterDescriptionInspector],
    responses={
        '403': "Nie masz uprawnień, by wykonać tę czynność.",
        '404': "Not found",
    },
    operation_description="Zwraca listę wszystkich CV zalogowanego użytkownika"
))
class UserCVListView(generics.ListAPIView):
    serializer_class = CVSerializer
    permission_classes = [IsStandardUser]
    filter_backends = (DjangoFilterBackend, CvOrderingFilter,)
    filterset_class = CVListFilter
    ordering_fields = ['date_created', 'was_reviewed', 'is_verified']
    ordering = ['-date_created']

    def get_queryset(self):
        user = self.request.user
        def_account = get_object_or_404(
            DefaultAccount.objects.filter(user=user))
        return CV.objects.filter(cv_user=def_account)


class UserCVNameView(views.APIView):
    permission_classes = [IsCVOwner]

    @swagger_auto_schema(
        operation_description='Zmienia nazwę danego CV',
        manual_parameters=[
            openapi.Parameter('cv_id', openapi.IN_PATH, type='string($uuid)',
                              description='String UUID będący id danego CV')
        ],
        request_body=openapi.Schema(type='object', properties={
            'name': openapi.Schema(type='string')}),

        responses={
            200: '"message": "Nazwa CV zmieniona na: nowa_nazwa"',
            403: 'Nie masz uprawnień do wykonania tej czynności',
            404: 'Nie znaleziono CV o podanym id',
            400: 'Nie podano nowej nazwy CV'
        }
    )
    def put(self, request, cv_id):
        try:
            cv = CV.objects.get(cv_id=cv_id)
            if not IsCVOwner().has_object_permission(request, self, cv):
                return ErrorResponse("Nie masz uprawnień do wykonania tej czynności", status.HTTP_403_FORBIDDEN)

        except CV.DoesNotExist:
            return ErrorResponse('Nie znaleziono CV o podanym id', status.HTTP_404_NOT_FOUND)

        try:
            cv.name = request.data['name']
            cv.save()
            return MessageResponse(f'Nazwa CV zmieniona na: {request.data["name"]}')
        except KeyError:
            return ErrorResponse('Nie podano nowej nazwy CV', status.HTTP_400_BAD_REQUEST)


class UserCVAvailabilityView(views.APIView):
    permission_classes = [IsStandardUser]

    @swagger_auto_schema(
        operation_description="Informuje, czy użytkownik może postować dalsze CV (tzn. czy ma ich mniej niż 5)",

        responses={
            200: '"can_post_cv" : True/False',
            403: 'User has no permission to perform this action.'
        }
    )
    def get(self, request):
        def_account = DefaultAccount.objects.get(user=request.user)
        users_cvs = CV.objects.filter(cv_user=def_account)
        if users_cvs.count() < 5:
            response_val = True
        else:
            response_val = False
        return Response({"can_post_cv" : response_val}, status=status.HTTP_200_OK)


class TemplatesListView(views.APIView):
    permission_classes = [IsStandardUser | IsAGuest]

    @swagger_auto_schema(
        operation_description="Lista możliwych templatek",
        responses={
            200: 'Lista templatek',
            403: 'Nie masz uprawnień do wykonania tej czynności',
        }
    )
    def get(self, request):
        templates = [k for (k, v) in TEMPLATES_CHOICES]
        return Response({"templates": templates}, status=status.HTTP_200_OK)

