from account.models import EmployerAccount, DefaultAccount
from account.permissions import IsEmployer
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from drf_yasg.openapi import Parameter, IN_PATH, IN_QUERY, Schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers
from rest_framework import status
from rest_framework import views
from rest_framework.decorators import permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from cv.models import CV
from .models import *
from .serializers import *
from rest_framework.generics import ListAPIView


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
            "offer_id": Schema(type='string', default='uuid4')
        }
    )


def sample_offer_response():
    return Schema(
        type='object',
        properties={
            'id': Schema(type='string', default="uuid4"),
            'offer_name': Schema(type='string', default="offer name"),
            'category': Schema(type='string', default="offer category"),
            'type': Schema(type='string', default="offer type"),
            'company_name': Schema(type='string', default="company name"),
            'company_address': Schema(type='string', default="company address"),
            'voivodeship': Schema(type='string', default="mazowieckie"),
            'expiration_date': Schema(type='string', default="2020-02-20"),
            'description': Schema(type='string', default="offer description")
        }
    )


def sample_paginated_offers_response():
    return Schema(type='object', properties={
        'count': Schema(type='integer', default=1),
        'next': Schema(type='string', default='"http://localhost:8000/job/job-offers/?page=2"'),
        'previous': Schema(type='string', default='null'),
        'results': Schema(type='array', items=sample_offer_response())
        },
    )


class OffersPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# Create your views here.
class JobOfferCreateView(views.APIView):

    @swagger_auto_schema(
        query_serializer=JobOfferSerializer,
        responses={
            '200': sample_offerid_response(),
            '401': sample_error_response('No authorization token'),
            '403': sample_error_response('No user or user is not employer'),
            '400': 'Bad request - serializer errors'
        },
        operation_description="Create job offer.",
    )
    @permission_classes([IsAuthenticated])
    def post(self, request):
        try:
            employer = EmployerAccount.objects.get(user=request.user)
            serializer = JobOfferSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.create(serializer.validated_data)
                instance.employer_id = employer.id
                instance.save()
                return OfferIdResponse(instance.id)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except EmployerAccount.DoesNotExist:
            return ErrorResponse("No user or user is not employer", status.HTTP_403_FORBIDDEN)


class JobOfferView(views.APIView):

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='integer')
        ],
        responses={
            '200': sample_message_response("Offer edited successfully"),
            '400': 'Bad request - serializer errors',
            '401': 'No authorization token',
            '404': sample_error_response('Offer not found'),
        },
        operation_description="Edit job offer.",
    )
    @permission_classes([IsAuthenticated])
    def post(self, request, offer_id):
        serializer = JobOfferEditSerializer(data=request.data)
        if serializer.is_valid():
            job_offer_edit = serializer.create(serializer.validated_data)
            try:
                instance = JobOffer.objects.get(pk=offer_id)
                fields_to_update = job_offer_edit.update_dict()
                for field, value in fields_to_update.items():
                    setattr(instance, field, value)
                instance.save()
                return MessageResponse("Offer edited successfully")
            except ObjectDoesNotExist:
                return ErrorResponse("Offer not found", status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='integer')
        ],
        responses={
            '200': JobOfferSerializer,
            '401': 'No authorization token',
            '404': sample_error_response('Offer not found'),
        },
        operation_description="Get job offer by id",
    )
    @permission_classes([IsAuthenticated])
    def get(self, request, offer_id):
        try:
            offer = JobOffer.objects.get(pk=offer_id)
            serializer = JobOfferSerializer(offer)
            return Response(serializer.data, status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return ErrorResponse("Offer not found", status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='integer')
        ],
        responses={
            '200': sample_message_response('Offer deleted'),
            '400': sample_error_response('Offer already removed'),
            '401': 'No authorization token',
            '404': sample_error_response('Offer not found')
        },
        operation_description="Set offer status to removed",
    )
    @permission_classes([IsAuthenticated])
    def delete(self, request, offer_id):
        try:
            instance = JobOffer.objects.get(pk=offer_id)
            if instance.removed:
                return ErrorResponse("Offer already removed", status.HTTP_400_BAD_REQUEST)
            instance.removed = True
            instance.save()
            return MessageResponse("Offer removed successfully")
        except ObjectDoesNotExist:
            return ErrorResponse("Offer not found", status.HTTP_404_NOT_FOUND)


@method_decorator(name='get', decorator=swagger_auto_schema(
    manual_parameters=[
        Parameter('page', IN_QUERY, description='Numer strony', type='integer', required=False),
        Parameter('page_size', IN_QUERY, description='Rozmiar strony, max 100', type='integer', required=False)
    ],
    query_serializer=JobOfferFiltersSerializer,
    responses={
        '200': sample_paginated_offers_response(),
        '400': "Bad request - serializer errors",
    },
    operation_description="Returns offers list with filters"
))
class JobOfferListView(generics.ListAPIView):
    serializer_class = JobOfferSerializer
    pagination_class = OffersPagination

    filter_serializer = None

    def get_queryset(self):
        job_offer_filters = self.filter_serializer.create(self.filter_serializer.validated_data)
        valid_filters = job_offer_filters.get_filters()
        return JobOffer.objects.filter(removed=False, **valid_filters)

    def get(self, request):
        self.filter_serializer = JobOfferFiltersSerializer(data=self.request.query_params)
        if self.filter_serializer.is_valid():
            return super().get(request)
        else:
            return Response(self.filter_serializer.errors, status.HTTP_400_BAD_REQUEST)


class CreateJobOfferApplicationView(views.APIView):

    @swagger_auto_schema(
        request_body=JobOfferApplicationSerializer,
        responses={
            '201': '"id": application.id',
            '400': 'Serializer errors',
            '403': "User is not a default user / User has already applied for this offer."
        },
        operation_description="Create a job application by specyfying cv and job_offer.",
    )
    def post(self, request):
        try:
            user = DefaultAccount.objects.get(user=request.user)
        except DefaultAccount.DoesNotExist:
            return Response("User is not a standard user", status.HTTP_403_FORBIDDEN)
       
        prev_app = JobOfferApplication.objects.filter(cv__cv_user=user, 
            job_offer__id=request.data['job_offer'])

        if prev_app:
             return Response("User has already applied for this offer", status.HTTP_403_FORBIDDEN)

        serializer = JobOfferApplicationSerializer(data=request.data)
        if serializer.is_valid():
            application = serializer.create(serializer.validated_data)
            response = {
                "id": application.id
            }
            return Response(response, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class JobOfferApplicationView(views.APIView):

    @swagger_auto_schema(
        responses={
            '200': JobOfferApplicationSerializer,
            '403': "User is not a standard user",
            '404': "This user has no application with given id"
        },
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='string($uuid)', 
                description='ID of an offer, for which the user has applied.')
        ],
        operation_description="Get current user's application for a particular job offer.",
    )
    def get(self, request, offer_id):
        try:
            user = DefaultAccount.objects.get(user=request.user)
        except DefaultAccount.DoesNotExist:
            return Response("User is not a standard user", status.HTTP_403_FORBIDDEN)

        application = JobOfferApplication.objects.filter(cv__cv_user=user, job_offer__id=offer_id)
        if not application:
             return Response("This user has no application with given id", status.HTTP_404_NOT_FOUND)

        serializer = JobOfferApplicationSerializer(application.first())
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            '200': "Application successfully deleted.",
            '403': "User is not a standard user",
            '404': "This user has no application with given id"
        },
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='string($uuid)', 
                description='ID of an offer, for which the user has applied.')
        ],
        operation_description="Delete current user's application for a particular job offer.",
    )
    def delete(self, request, offer_id):
        try:
            user = DefaultAccount.objects.get(user=request.user)
        except DefaultAccount.DoesNotExist:
            return Response("User is not a standard user", status.HTTP_403_FORBIDDEN)

        application = JobOfferApplication.objects.filter(cv__cv_user=user, job_offer__id=offer_id)
        
        if not application:
             return Response("This user has no application with given id", status.HTTP_404_NOT_FOUND)

        application.delete()
        return Response("Application successfully deleted.", status.HTTP_200_OK)

@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        '200': JobOfferApplicationSerializer(many=True),
        '404': "Not found",
    },
    manual_parameters=[
        Parameter('offer_id', IN_PATH, type='string($uuid)', 
                description='ID of the offer, for which users have applied.')
    ],
    operation_description="Returns the list of applications for a job offer."
))
class EmployerApplicationListView(ListAPIView):
    serializer_class = JobOfferApplicationSerializer
    permission_classes = [IsEmployer]

    def get_queryset(self):
        id = self.kwargs['offer_id']
        return JobOfferApplication.objects.filter(job_offer=id)

@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        '200': JobOfferApplicationSerializer(many=True),
        '404': "Not found",
    },
    operation_description="Returns the list of user's job applications."
))
class UserApplicationsView(ListAPIView):
    serializer_class = JobOfferApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JobOfferApplication.objects.filter(cv__cv_user__user=self.request.user)


@method_decorator(name='get', decorator=swagger_auto_schema(
    query_serializer=JobOfferFiltersSerializer,
    manual_parameters=[
        Parameter('page', IN_QUERY, description='Numer strony', type='integer', required=False),
        Parameter('page_size', IN_QUERY, description='Rozmiar strony, max 100', type='integer', required=False)
    ],
    responses={
        '200': sample_paginated_offers_response(),
        '401': 'No authorization token',
        '403': sample_error_response('No user or user is not employer'),
        '404': "Bad request - serializer errors",
    },
    operation_description="Returns offers list with filters for current employer"
))
class EmployerJobOffersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobOfferSerializer
    pagination_class = OffersPagination

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
            return ErrorResponse("No user or user is not employer", status.HTTP_403_FORBIDDEN)


class VoivodeshipsEnumView(views.APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={
            '200': Schema(type='object', properties={
                "voivodeships": Schema(type='array', items=Schema(type='string', default=['w1', 'w2', '...']))
            })
        },
        operation_description="returns list of possible voivodeship values",
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
        operation_description="Returns list of all categories."
    )
    def get(self, request):
        response = {"categories": list(JobOfferCategory.objects.values_list('name', flat=True))}
        return Response(response, status=status.HTTP_200_OK)


class JobOfferTypesListView(generics.ListAPIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={
            '200': Schema(type='object', properties={
                "offer_types": Schema(type='array', items=Schema(type='string', default=['t1', 't2', '...']))
            })
        },
        operation_description="Returns list of all types."
    )
    def get(self, request):
        response = {"offer_types": list(JobOfferType.objects.values_list('name', flat=True))}
        return Response(response, status=status.HTTP_200_OK)
