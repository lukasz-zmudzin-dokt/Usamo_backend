import os
from notifications.signals import notify
from rest_framework.parsers import MultiPartParser
from account.models import EmployerAccount, DefaultAccount, Account
from account.permissions import *
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.inspectors import DjangoRestResponsePagination
from drf_yasg.openapi import Parameter, IN_PATH, IN_QUERY, Schema, IN_BODY, IN_FORM
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers, filters, status, views
from rest_framework.decorators import permission_classes
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from cv.models import CV
from .filters import JobOfferApplicationListFilter, JobOfferApplicationOrderingFilter, DjangoFilterDescriptionInspector, \
    JobOfferOrderingFilter
from .models import *
from .serializers import *
from rest_framework.generics import ListAPIView, get_object_or_404


class ErrorResponse(Response):
    def __init__(self, error_message, status_code):
        super().__init__(data={"error": error_message}, status=status_code)


def sample_error_response(error_message):
    return Schema(
        type='object',
        properties={
            "error": Schema(type='string', default=error_message)
        }
    )


class MessageResponse(Response):
    def __init__(self, message):
        super().__init__(data={"message": message}, status=status.HTTP_200_OK)


def sample_message_response(message):
    return Schema(
        type='object',
        properties={
            "message": Schema(type='string', default=message)
        }
    )


class OfferIdResponse(Response):
    def __init__(self, offer_id):
        super().__init__(data={"offer_id": offer_id}, status=status.HTTP_200_OK)


def sample_offerid_response():
    return Schema(
        type='object',
        properties={
            "offer_id": Schema(type='string', default='uuid4', format='byte')
        }
    )


class OffersPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ApplicationsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# Create your views here.
class JobOfferCreateView(views.APIView):
    permission_classes = [IsEmployer]

    @swagger_auto_schema(
        request_body=JobOfferSerializer,
        responses={
            '200': sample_offerid_response(),
            '401': sample_error_response('No authorization token'),
            '403': sample_error_response('Brak użytkownika lub użytkownik nie jest pracodawcą'),
            '400': 'Błędy walidacji (np. brakujące pole)'
        },
        operation_description="Pozwala stworzyć ofertę pracy.",
    )
    def post(self, request):
        try:
            employer = EmployerAccount.objects.get(user=request.user)
            serializer = JobOfferSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.create(serializer.validated_data)
                instance.employer_id = employer.id
                instance.save()
                notify.send(employer.user, recipient=Account.objects.filter(groups__name__contains='staff_jobs'),
                            verb=f'Użytkownik {employer.user.username} utworzył_a nową ofertę pracy',
                            app='offerApproval',
                            object_id=None
                            )
                return OfferIdResponse(instance.id)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except EmployerAccount.DoesNotExist:
            return ErrorResponse("Brak użytkownika lub użytkownik nie jest pracodawcą", status.HTTP_403_FORBIDDEN)


class JobOfferView(views.APIView):
    permission_classes = [GetRequestPublicPermission |
                          IsEmployer | IsStaffResponsibleForJobs]

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='string', format='byte')
        ],
        operation_id='job_job-offer_edit',
        request_body=JobOfferSerializer,
        responses={
            '200': sample_message_response("Pomyślnie edytowano ofertę"),
            '400': 'Błędy walidacji (np. brakujące pole)',
            '401': 'No authorization token',
            '403': 'Nie masz uprawnień do wykonania tej czynności',
            '404': sample_error_response('Nie znaleziono oferty'),
        },
        operation_description="Edytuje ofertę pracy",
    )
    def put(self, request, offer_id):
        def validate_update(inst, valid_serializer):
            data = valid_serializer.validated_data
            salary_min = data.get('salary_min')
            salary_max = data.get('salary_max')
            if salary_min and salary_max and salary_min > salary_max:
                return ErrorResponse("Minimalne wynagrodzenie jest większe niż maksymalne wynagrodzenie", status.HTTP_400_BAD_REQUEST)
            elif salary_min and not salary_max and salary_min > inst.salary_max:
                return ErrorResponse("Podane minimalne wynagrodzenie jest większe niż aktualne maksymalne wynagrodzenie", status.HTTP_400_BAD_REQUEST)
            elif not salary_min and salary_max and salary_max < inst.salary_min:
                return ErrorResponse("Podane maskymalne wynagrodzenie jest mniejsze niż aktualne minimalne wynagrodzenie", status.HTTP_400_BAD_REQUEST)
            valid_serializer.update(inst, data)
            return MessageResponse("Pomyślnie edytowano ofertę")

        try:
            instance = JobOffer.objects.get(pk=offer_id)
        except ObjectDoesNotExist:
            return ErrorResponse("Nie znaleziono oferty", status.HTTP_404_NOT_FOUND)
        serializer = JobOfferSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            if not IsEmployer().has_object_permission(request, self, instance) \
                    and not IsStaffResponsibleForJobs().has_object_permission(request, self, instance):
                return ErrorResponse("Nie masz uprawnień do wykonania tej czynności", status.HTTP_403_FORBIDDEN)
            return validate_update(instance, serializer)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='string', format='byte')
        ],
        responses={
            '200': JobOfferSerializer,
            '401': 'No authorization token',
            '404': sample_error_response('Nie znaleziono oferty'),
        },
        operation_description="Zwraca szczegóły oferty pracy po id",
    )
    def get(self, request, offer_id):
        try:
            offer = JobOffer.objects.get(pk=offer_id)
            serializer = JobOfferSerializer(offer)
            return Response(serializer.data, status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return ErrorResponse("Nie znaleziono oferty", status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='string', format='byte')
        ],
        responses={
            '200': sample_message_response("Oferta została pomyślnie usunięta."),
            '400': sample_error_response('Oferta została wcześniej usunięta'),
            '401': 'No authorization token',
            '403': sample_error_response('Nie masz uprawnień do wykonania tej czynności'),
            '404': sample_error_response('Nie znaleziono oferty')
        },
        operation_description="Zmienia status oferty na removed",
    )
    def delete(self, request, offer_id):
        try:
            instance = JobOffer.objects.get(pk=offer_id)
            if not IsEmployer().has_object_permission(request, self, instance) \
                    and not IsStaffResponsibleForJobs().has_object_permission(request, self, instance):
                return ErrorResponse("Nie masz uprawnień do wykonania tej czynności", status.HTTP_403_FORBIDDEN)
            if instance.removed:
                return ErrorResponse("Oferta została wcześniej usunięta", status.HTTP_400_BAD_REQUEST)
            instance.removed = True
            instance.save()
            if IsStaffResponsibleForJobs().has_object_permission(request, self, instance):
                notify.send(request.user, recipient=instance.employer.user,
                            verb=f'Twoja oferta pracy została usunięta',
                            app='myOffers',
                            object_id=None
                            )
            return MessageResponse("Oferta została pomyślnie usunięta.")
        except ObjectDoesNotExist:
            return ErrorResponse("Nie znaleziono oferty", status.HTTP_404_NOT_FOUND)


class JobOfferImageView(views.APIView):
    permission_classes = [IsEmployer | IsStaffResponsibleForJobs]
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='string($uuid)'),
            Parameter('file', IN_FORM, type='file')
        ],
        responses={
            '200': sample_message_response('Poprawnie dodano zdjęcie do oferty pracy'),
            '401': sample_error_response('No authorization token'),
            '403': sample_error_response('Brak uprawnień do tej czynności'),
            '400': "Błędy walidacji (np. brakujące pole)"
        },
        operation_description="Api do uploadu dodatkowego zdjęcia do oferty pracy.",
    )
    def post(self, request, offer_id):
        try:
            image = request.FILES['file']
        except MultiValueDictKeyError:
            return ErrorResponse('Nie znaleziono pliku. Upewnij się, że został on załączony pod kluczem file',
                status.HTTP_400_BAD_REQUEST)
        try:
            instance = JobOffer.objects.get(pk=offer_id)
        except ObjectDoesNotExist:
            return ErrorResponse("Nie znaleziono oferty", status.HTTP_404_NOT_FOUND)
        if not IsEmployer().has_object_permission(request, self, instance) \
                and not IsStaffResponsibleForJobs().has_object_permission(request, self, instance):
            return ErrorResponse("Nie masz uprawnień, by wykonać tę czynność.", status.HTTP_403_FORBIDDEN)
        message = 'Poprawnie dodano zdjęcie do oferty pracy'
        if instance.offer_image:
            message = 'Poprawnie zmieniono zdjęcie do oferty pracy'
            os.remove(instance.offer_image.path)

        instance.offer_image = image
        instance.save()
        return MessageResponse(message)

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='string', format='byte')
        ],
        responses={
            '200': "Usunięto zdjęcie z oferty pracy",
            '401': sample_error_response('No authorization token'),
            '403': sample_error_response('Brak uprawnień do tej czynności'),
            '404': sample_error_response('Nie znaleziono oferty/Brak zdjęcia dla tej oferty')
        },
        operation_description="Usuwanie typu oferty pracy",
    )
    def delete(self, request, offer_id):
        try:
            instance = JobOffer.objects.get(pk=offer_id)
        except ObjectDoesNotExist:
            return ErrorResponse("Nie znaleziono oferty", status.HTTP_404_NOT_FOUND)
        if not IsEmployer().has_object_permission(request, self, instance) \
                and not IsStaffResponsibleForJobs().has_object_permission(request, self, instance):
            return ErrorResponse("No permissions for this action", status.HTTP_403_FORBIDDEN)
        if not instance.offer_image:
            return ErrorResponse('Brak zdjęcia dla tej oferty', status.HTTP_404_NOT_FOUND)
        os.remove(instance.offer_image.path)
        instance.offer_image = None
        instance.save()
        return MessageResponse('Usunięto zdjęcie z oferty pracy')


@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[DjangoFilterDescriptionInspector],
    query_serializer=JobOfferFiltersSerializer,
    responses={
        '400': "Błędy walidacji (np. brakujące pole)",
    },
    operation_description="Zwraca listę ofert pracy z możliwością filtracji"
))
class JobOfferListView(generics.ListAPIView):
    serializer_class = JobOfferSerializer
    pagination_class = OffersPagination
    filter_backends = [JobOfferOrderingFilter]
    ordering_fields = ['offer_name', 'category', 'voivodeship', 'salary_min', 'salary_max', 'company_name',
                       'expiration_date']
    ordering = ['expiration_date']
    permission_classes = [AllowAny]

    filter_serializer = None

    def get_queryset(self):
        job_offer_filters = self.filter_serializer.create(self.filter_serializer.validated_data)
        valid_filters = job_offer_filters.get_filters()
        return JobOffer.objects.select_related('employer')\
            .select_related('category')\
            .select_related('offer_type')\
            .select_related('company_address')\
            .filter(removed=False, confirmed=True, **valid_filters)

    def get(self, request):
        self.filter_serializer = JobOfferFiltersSerializer(data=self.request.query_params)
        if self.filter_serializer.is_valid():
            return super().get(request)
        else:
            return Response(self.filter_serializer.errors, status.HTTP_400_BAD_REQUEST)


class CreateJobOfferApplicationView(views.APIView):
    permission_classes = [IsStandardUser]

    @swagger_auto_schema(
        request_body=JobOfferApplicationSerializer,
        responses={
            '201': '"id": application.id',
            '400': 'Błędy walidacji (np. brakujące pole)',
            '403': "You do not have permission to perform this action. / Aplikowałeś_aś już na tę ofertę \
                /  CV o podanym id nie należy do Ciebie"
        },
        operation_description="Tworzy aplikację na pracę z podaną ofertą pracy oraz id cv",
    )
    def post(self, request):
        user = DefaultAccount.objects.get(user=request.user)
        try:
            try:
                CV.objects.get(cv_user=user, cv_id=request.data['cv'])
            except KeyError:
                return ErrorResponse('Należy podać, jakie CV złożyć w aplikacji', status.HTTP_400_BAD_REQUEST)
        except CV.DoesNotExist:
            return ErrorResponse("CV o podanym id nie należy do Ciebie", status.HTTP_403_FORBIDDEN)

        prev_app = JobOfferApplication.objects.filter(cv__cv_user=user, 
            job_offer__id=request.data['job_offer'])

        if prev_app:
             return ErrorResponse("Aplikowałeś_aś już na tę ofertę", status.HTTP_403_FORBIDDEN)

        serializer = JobOfferApplicationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                application = serializer.create(serializer.validated_data)
            except FileNotFoundError:
                return ErrorResponse("Nie znaleziono pliku zawierającego CV", status.HTTP_404_NOT_FOUND)
            response = {
                "id": application.id
            }
            job_offer = JobOffer.objects.get(id=request.data['job_offer'])
            
            notify.send(user.user, recipient=job_offer.employer.user,

                        verb=f'Użytkownik {user.user.username} aplikował_a na Twoją ofertę pracy!',
                        app='myOffers',
                        object_id=None
                        )
            return Response(response, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class JobOfferApplicationView(views.APIView):
    permission_classes = [IsStandardUser]

    @swagger_auto_schema(
        responses={
            '200': JobOfferApplicationSerializer,
            '403': "You do not have permission to perform this action.",
            '404': "Nie posiadasz takiej aplikacji"
        },
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='string($uuid)', 
                description='ID oferty, na którą aplikował obecny użytkownik')
        ],
        operation_description="Zwraca aplikację obecnego użytkownika na daną ofertę pracy",
    )
    def get(self, request, offer_id):
        user = DefaultAccount.objects.get(user=request.user)
        application = JobOfferApplication.objects.filter(cv__cv_user=user, job_offer__id=offer_id)
        if not application:
             return ErrorResponse("Nie posiadasz takiej aplikacji", status.HTTP_404_NOT_FOUND)

        serializer = JobOfferApplicationSerializer(application.first())
        return Response(serializer.data, status.HTTP_200_OK)


@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[DjangoFilterDescriptionInspector],
    responses={
        '403': "Oferta nie należy do Ciebie",
        '404': "Nie znaleziono oferty"
    },
    manual_parameters=[
        Parameter('offer_id', IN_PATH, type='string($uuid)', 
                description='ID oferty, na którą użytkownicy aplikowali')
    ],
    operation_description="Zwraca listę aplikacji na daną ofertę pracy"
))
class EmployerApplicationListView(ListAPIView):
    serializer_class = JobOfferApplicationSerializer
    permission_classes = [IsEmployer]
    filter_backends = (DjangoFilterBackend, JobOfferApplicationOrderingFilter)
    filterset_class = JobOfferApplicationListFilter
    ordering_fields = ['first_name', 'last_name', 'email', 'date_posted', 'was_read']
    ordering = ['-date_posted']
    pagination_class = ApplicationsPagination

    def get_queryset(self):
        id = self.kwargs['offer_id']
        return JobOfferApplication.objects.filter(job_offer=id)

    def get(self, request, offer_id):
        try:
            offer = JobOffer.objects.get(id=offer_id)
            if IsEmployer().has_object_permission(request, self, offer):
                return super().get(request)
            else:
                return ErrorResponse("Oferta nie należy do Ciebie", status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return ErrorResponse("Nie znaleziono oferty", status.HTTP_404_NOT_FOUND)

@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[DjangoFilterDescriptionInspector],
    responses={
        '403': "You do not have permission to perform this action.",
        '404': "Not found",
    },
    operation_description="Zwraca listę aplikacji danego użytkownika"
))
class UserApplicationsView(ListAPIView):
    serializer_class = JobOfferApplicationSerializer
    permission_classes = [IsStandardUser]
    filter_backends = (DjangoFilterBackend, JobOfferApplicationOrderingFilter)
    filterset_class = JobOfferApplicationListFilter
    ordering_fields = ['first_name', 'last_name', 'email', 'date_posted', 'was_read']
    ordering = ['-date_posted']
    pagination_class = ApplicationsPagination

    def get_queryset(self):
        return JobOfferApplication.objects.filter(cv__cv_user__user=self.request.user)


class EmployerApplicationMarkAsReadView(views.APIView):
    permission_classes = [IsEmployer]

    @swagger_auto_schema(
        responses={
            '200': sample_message_response("Aplikacja została oznaczona jako przeczytana"),
            '403': sample_error_response("Aplikacja nie została złożona na ofertę należącą Ciebie"),
            '404': sample_error_response("Nie znaleziono aplikacji o podanym id")
        },
        manual_parameters=[
            Parameter('application_id', IN_PATH, type='string($uuid)',
                description='ID aplikacji na ofertę pracy')
        ],
        operation_description="Pozwala oznaczyć aplikację jako przeczytaną"
    )
    def post(self, request, application_id):
        try:
            application = JobOfferApplication.objects.get(id=application_id)
        except JobOfferApplication.DoesNotExist:
            return ErrorResponse("Nie znaleziono aplikacji o podanym id", status.HTTP_404_NOT_FOUND)

        offer = application.job_offer
        if not IsEmployer().has_object_permission(request, self, offer):
            return ErrorResponse("Aplikacja nie została złożona na ofertę należącą do \
                                Ciebie", status.HTTP_403_FORBIDDEN)

        application.was_read = True
        application.save()

        return MessageResponse("Aplikacja została oznaczona jako przeczytana")


class EmployerApplicationMarkAsUnreadView(views.APIView):
    permission_classes = [IsEmployer]

    @swagger_auto_schema(
        responses={
            '200': sample_message_response("Aplikacja została oznaczona jako nieprzeczytana"),
            '403': sample_error_response("Aplikacja nie została złożona na ofertę należącą Ciebie"),
            '404': sample_error_response("Nie znaleziono aplikacji o podanym id")
        },
        manual_parameters=[
            Parameter('application_id', IN_PATH, type='string($uuid)',
                description='ID aplikacji na ofertę pracy')
        ],
        operation_description="Pozwala oznaczyć aplikację jako przeczytaną"
    )
    def post(self, request, application_id):
        try:
            application = JobOfferApplication.objects.get(id=application_id)
        except JobOfferApplication.DoesNotExist:
            return ErrorResponse("Nie znaleziono aplikacji o podanym id", status.HTTP_404_NOT_FOUND)

        offer = application.job_offer
        if not IsEmployer().has_object_permission(request, self, offer):
            return ErrorResponse("Aplikacja nie została złożona na ofertę należącą do \
                                Ciebie", status.HTTP_403_FORBIDDEN)

        application.was_read = False
        application.save()

        return MessageResponse("Aplikacja została oznaczona jako nieprzeczytana")


@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[DjangoFilterDescriptionInspector],
    query_serializer=JobOfferFiltersSerializer,
    responses={
        '401': 'No authorization token',
        '403': "You do not have permission to perform this action.",
        '404': "Błędy walidacji (np. brakujące pole)",
    },
    operation_description="Zwraca listę ofert pracy z możliwością filtracji dla obecnego pracodawcy"
))
class EmployerJobOffersView(generics.ListAPIView):
    permission_classes = [IsEmployer]
    serializer_class = JobOfferSerializer
    pagination_class = OffersPagination
    filter_backends = [JobOfferOrderingFilter]
    ordering_fields = ['offer_name', 'category', 'voivodeship', 'salary_min', 'salary_max', 'company_name',
                       'expiration_date']
    ordering = ['expiration_date']

    filter_serializer = None
    employer = None

    def get_queryset(self):
        job_offer_filters = self.filter_serializer.create(self.filter_serializer.validated_data)
        valid_filters = job_offer_filters.get_filters()
        return JobOffer.objects.filter(removed=False, employer_id=self.employer.id, **valid_filters)

    def get(self, request):
        self.filter_serializer = JobOfferFiltersSerializer(data=self.request.data)
        try:
            self.employer = EmployerAccount.objects.get(user_id=self.request.user.id)
            if self.filter_serializer.is_valid():
                return super().get(request)
            else:
                return Response(self.filter_serializer.errors, status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return ErrorResponse("Brak użytkownika lub użytkownik nie jest pracodawcą", status.HTTP_403_FORBIDDEN)


@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[DjangoFilterDescriptionInspector],
    query_serializer=JobOfferFiltersSerializer,
    responses={
        '401': 'No authorization token',
        '403': sample_error_response('Brak uprawnień do tej czynności'),
        '400': sample_error_response('Błędy walidacji (np. brakujące pole)'),
    },
    operation_description="Zwraca listę niepotwierdzonych ofert pracy z możliwością filtracji"
))
class AdminUnconfirmedJobOffersView(generics.ListAPIView):
    serializer_class = JobOfferSerializer
    pagination_class = OffersPagination
    permission_classes = [IsStaffResponsibleForJobs]
    filter_backends = [JobOfferOrderingFilter]
    ordering_fields = ['offer_name', 'category', 'voivodeship', 'salary_min', 'salary_max', 'company_name',
                       'expiration_date']
    ordering = ['expiration_date']

    filter_serializer = None

    def get_queryset(self):
        job_offer_filters = self.filter_serializer.create(self.filter_serializer.validated_data)
        valid_filters = job_offer_filters.get_filters()
        return JobOffer.objects.filter(removed=False, confirmed=False, **valid_filters)

    def get(self, request):
        self.filter_serializer = JobOfferFiltersSerializer(data=self.request.data)
        if self.filter_serializer.is_valid():
            return super().get(request)
        else:
            return Response(self.filter_serializer.errors, status.HTTP_400_BAD_REQUEST)


class AdminConfirmJobOfferView(views.APIView):
    permission_classes = [IsStaffResponsibleForJobs]

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='string', format='byte')
        ],
        request_body=Schema(type='object', properties={
            'confirmed': Schema(type='boolean')
        }),
        responses={
            '200': sample_message_response('Ustawiono potwierdzenie oferty pracy'),
            '400': sample_error_response('Oferta jest usunięta'),
            '401': 'No authorization token',
            '403': sample_error_response('Brak uprawnień do tej czynności'),
            '404': sample_error_response('Nie znaleziono oferty')
        },
        operation_description="Ustawianie potwierdzenia ofert pracy",
    )
    def post(self, request, offer_id):
        try:
            instance = JobOffer.objects.get(pk=offer_id)
        except ObjectDoesNotExist:
            return ErrorResponse("Nie znaleziono oferty", status.HTTP_404_NOT_FOUND)
        if instance.removed:
            return ErrorResponse("Oferta jest usunięta", status.HTTP_400_BAD_REQUEST)
        if 'confirmed' in request.data:
            confirmed = request.data['confirmed']
            instance.confirmed = confirmed
            instance.save()
            notify.send(request.user, recipient=instance.employer.user,
                        verb=f'Twoja oferta pracy została zatwierdzona',
                        app='myOffers',
                        object_id=None
                        )
            return MessageResponse("Ustawiono potwierdzenie oferty pracy")
        return ErrorResponse("Błędy walidacji (np. brakujące pole)", status.HTTP_400_BAD_REQUEST)


class VoivodeshipsEnumView(views.APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={
            '200': Schema(type='object', properties={
                "voivodeships": Schema(type='array', items=Schema(type='string', default=['w1', 'w2', '...']))
            })
        },
        operation_description="Zwraca listę województw",
    )
    def get(self, request):
        response = {"voivodeships": Voivodeships().getKeys()}
        return Response(response, status=status.HTTP_200_OK)


class JobOfferCategoryListView(views.APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={
            '200': Schema(type='object', properties={
                "categories": Schema(type='array', items=Schema(type='string', default=['c1', 'c2', '...']))
            })
        },
        operation_description="Zwraca listę wszystkich kategorii"
    )
    def get(self, request):
        response = {"categories": list(JobOfferCategory.objects.values_list('name', flat=True))}
        return Response(response, status=status.HTTP_200_OK)


class JobOfferCategoryView(views.APIView):
    permission_classes = [IsStaffResponsibleForJobs]

    @swagger_auto_schema(
        request_body=JobOfferCategorySerializer,
        responses={
            '200': 'Branża ofert pracy utworzona',
            '401': sample_error_response('No authorization token'),
            '403': sample_error_response('Brak uprawnień do tej czynności'),
            '400': 'Błędy walidacji (np. brakujące pole)'
        },
        operation_description="Tworzenie branży ofert pracy",
    )
    def post(self, request):
        serializer = JobOfferCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return MessageResponse('Branża ofert pracy dodana')
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=JobOfferCategorySerializer,
        responses={
            '200': "Branża ofert pracy usunięta",
            '401': sample_error_response('No authorization token'),
            '403': sample_error_response('Brak uprawnień do tej czynności'),
            '400': 'Błędy walidacji (np. brakujące pole)',
            '404': sample_error_response('Nie znaleziono takiej branży ofert pracy')
        },
        operation_description="Usuwanie branży ofert pracy",
    )
    def delete(self, request):
        serializer = JobOfferCategorySerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            try:
                JobOfferCategory.objects.get(pk=name).delete()
            except ObjectDoesNotExist:
                return ErrorResponse("Nie znaleziono takiej branży ofert pracy", status.HTTP_404_NOT_FOUND)
            return MessageResponse("Branża ofert pracy usunięta")
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class JobOfferTypesListView(views.APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={
            '200': Schema(type='object', properties={
                "offer_types": Schema(type='array', items=Schema(type='string', default=['t1', 't2', '...']))
            })
        },
        operation_description="Zwraca listę wszystkich typów"
    )
    def get(self, request):
        response = {"offer_types": list(JobOfferType.objects.values_list('name', flat=True))}
        return Response(response, status=status.HTTP_200_OK)


class JobOfferTypeView(views.APIView):
    permission_classes = [IsStaffResponsibleForJobs]

    @swagger_auto_schema(
        request_body=JobOfferTypeSerializer,
        responses={
            '200': 'Typ oferty pracy utworzony',
            '401': sample_error_response('No authorization token'),
            '403': sample_error_response('Brak uprawnień do tej czynności'),
            '400': 'Błędy walidacji (np. brakujące pole)'
        },
        operation_description="Tworzenie typu oferty pracy",
    )
    def post(self, request):
        serializer = JobOfferTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return MessageResponse('Typ oferty pracy dodany')
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=JobOfferTypeSerializer,
        responses={
            '200': "Typ oferty pracy usunięty",
            '401': sample_error_response('No authorization token'),
            '403': sample_error_response('Brak uprawnień do tej czynności'),
            '400': 'Błędy walidacji (np. brakujące pole)',
            '404': sample_error_response('Nie znaleziono takiego typu oferty pracy')
        },
        operation_description="Usuwanie typu oferty pracy",
    )
    def delete(self, request):
        serializer = JobOfferTypeSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            try:
                JobOfferType.objects.get(pk=name).delete()
            except ObjectDoesNotExist:
                return ErrorResponse("Nie znaleziono takiego typu oferty pracy", status.HTTP_404_NOT_FOUND)
            return MessageResponse("Typ oferty pracy usunięty")
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class GetZipFileView(views.APIView):
    permission_classes = [IsEmployer]

    @swagger_auto_schema(
        responses={
            '200': '"url": ścieżka-do-pliku-zip',
            '401': '"detail": Nie podano danych uwierzytelniających.',
            '403': sample_error_response('Oferta nie należy do Ciebie'),
            '404': sample_error_response('Nie znaleziono oferty')
        },
        operation_description="Zwraca pracodawcy plik zip ze spakowanymi plikami CV wszystkich użytkowników, "
                              "którzy aplikowali na daną ofertę",
    )
    def get(self, request, offer_id):
        try:
            offer = JobOffer.objects.get(id=offer_id)
            if IsEmployer().has_object_permission(request, self, offer):
                offer.generate_zip()
                return Response({"url": offer.zip_file}, status=status.HTTP_200_OK)
            else:
                return ErrorResponse("Oferta nie należy do Ciebie", status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return ErrorResponse("Nie znaleziono oferty", status.HTTP_404_NOT_FOUND)