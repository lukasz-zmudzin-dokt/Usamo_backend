from account.models import EmployerAccount, DefaultAccount
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from drf_yasg.openapi import Parameter, IN_PATH, IN_QUERY, Schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework import status
from rest_framework import views
from rest_framework.decorators import permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .models import JobOffer
from .serializers import JobOfferSerializer, JobOfferEditSerializer, JobOfferFiltersSerializer, \
    InterestedUserSerializer, Voivodeships


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
            employer = EmployerAccount.objects.get(user_id=request.user.id)
            serializer = JobOfferSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.create(serializer.validated_data)
                instance.employer_id = employer.id
                instance.save()
                return OfferIdResponse(instance.id)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
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
        self.filter_serializer = JobOfferFiltersSerializer(data=self.request.data)
        if self.filter_serializer.is_valid():
            return super().get(request)
        else:
            return Response(self.filter_serializer.errors, status.HTTP_400_BAD_REQUEST)


class JobOfferInterestedUsersView(views.APIView):

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='integer')
        ],
        responses={
            '200': sample_message_response("Added to interested users"),
            '400': sample_error_response("User already added"),
            '401': 'No authorization token',
            '403': sample_error_response('No user or user is not default user'),
            '404': sample_error_response("Offer not found"),
        },
        operation_description="Adding user to offer interested users.",
    )
    @permission_classes([IsAuthenticated])
    def post(self, request, offer_id):
        try:
            user = DefaultAccount.objects.get(user_id=request.user.id)
            try:
                instance = JobOffer.objects.get(pk=offer_id)
                if instance.interested_users.filter(id=user.id).exists():
                    return ErrorResponse("User already added", status.HTTP_400_BAD_REQUEST)
                instance.interested_users.add(user)
                instance.save()
                return MessageResponse("Added to interested users")
            except ObjectDoesNotExist:
                return ErrorResponse("Offer not found", status.HTTP_404_NOT_FOUND)
        except ObjectDoesNotExist:
            return ErrorResponse("No user or user is not default user", status.HTTP_403_FORBIDDEN)


class EmployerJobOfferInterestedUsersView(views.APIView):

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='integer')
        ],
        responses={
            '200': InterestedUserSerializer,
            '401': 'No authorization token',
            '404': sample_error_response("Offer not found"),
        },
        operation_description="Get offer interested users.",
    )
    @permission_classes([IsAuthenticated])
    def get(self, request, offer_id):
        try:
            instance = JobOffer.objects.get(pk=offer_id)
            serializer = InterestedUserSerializer(instance.interested_users, many=True)
            return Response(serializer.data, status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return ErrorResponse("Offer not found", status.HTTP_404_NOT_FOUND)


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

    @swagger_auto_schema(
        responses={
            '200': Schema(type='object', properties={
                "voivodeships": Schema(type='array', items=Schema(type='string', default=['w1', 'w2', '...']))
            }),
            '401': 'No authorization token'
        },
        operation_description="returns list of possible voivodeship values",
    )
    @permission_classes([IsAuthenticated])
    def get(self, request):
        response = {"voivodeships": Voivodeships().getKeys()}
        return Response(response, status=status.HTTP_200_OK)

