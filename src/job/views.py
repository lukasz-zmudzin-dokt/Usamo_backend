from account.models import EmployerAccount, DefaultAccount
from account.permissions import IsEmployer, IsDefaultUser
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from drf_yasg.openapi import Parameter, IN_PATH
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework import status
from rest_framework import views
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .models import JobOffer
from .serializers import JobOfferSerializer, JobOfferEditSerializer, JobOfferFiltersSerializer, InterestedUserSerializer


# Create your views here.
class JobOfferCreateView(views.APIView):

    @swagger_auto_schema(
        query_serializer=JobOfferSerializer,
        responses={
            '200': 'OK',
            '401': 'No authorization token',
            '403': 'No user or user is not employer',
            '400': 'Bad request'
        },
        operation_description="Create job offer.",
    )
    @permission_classes([IsAuthenticated & IsEmployer])
    def post(self, request):
        try:
            employer = EmployerAccount.objects.get(user_id=request.user.id)
            serializer = JobOfferSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.create(serializer.validated_data)
                instance.employer_id = employer.id
                instance.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response("No user or user is not employer", status=status.HTTP_403_FORBIDDEN)


class JobOfferView(views.APIView):

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='integer')
        ],
        responses={
            '200': 'OK',
            '400': 'Bad request',
            '401': 'No authorization token',
            '403': 'No user or user is not employer or offer not belongs to employer',
            '404': "Offer not found",
        },
        operation_description="Edit job offer.",
    )
    @permission_classes([IsAuthenticated & (IsEmployer | IsAdminUser)])
    def post(self, request, offer_id):
        serializer = JobOfferEditSerializer(data=request.data)
        if serializer.is_valid():
            job_offer_edit = serializer.create(serializer.validated_data)
            try:
                instance = JobOffer.objects.get(pk=offer_id)
                is_admin = request.user.is_admin
                is_employer = EmployerAccount.objects.filter(id=instance.employer_id, user_id=request.user.id).exists()
                if is_admin or is_employer:
                    fields_to_update = job_offer_edit.update_dict()
                    for field, value in fields_to_update.items():
                        setattr(instance, field, value)
                    instance.save()
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response("Offer not belongs to employer", status=status.HTTP_403_FORBIDDEN)
            except ObjectDoesNotExist:
                return Response("Offer not found", status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='integer')
        ],
        responses={
            '200': 'Interested users',
            '401': 'No authorization token',
            '404': "Offer not found",
        },
        operation_description="Get job offer by id",
    )
    @permission_classes([IsAuthenticated])
    def get(self, request, offer_id):
        try:
            offer = JobOffer.objects.get(pk=offer_id)
            serializer = JobOfferSerializer(offer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response("Offer not found", status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='integer')
        ],
        responses={
            '200': 'Offer deleted',
            '401': 'No authorization token',
            '403': 'No user or user is not employer or offer not belongs to employer',
            '404': "Offer not found"
        },
        operation_description="Set offer status to removed",
    )
    @permission_classes([IsAuthenticated & IsEmployer])
    def delete(self, request, offer_id):
        try:
            instance = JobOffer.objects.get(pk=offer_id)
            is_admin = request.user.is_admin
            is_employer = EmployerAccount.objects.filter(id=instance.employer_id, user_id=request.user.id).exists()
            if is_admin or is_employer:
                instance.removed = True
                instance.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response("Offer not belongs to employer", status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response("Offer not found", status.HTTP_404_NOT_FOUND)


@method_decorator(name='get', decorator=swagger_auto_schema(
    query_serializer=JobOfferFiltersSerializer,
    responses={
        '200': 'List of offers',
        '404': "Bad request",
    },
    operation_description="Returns offers list with filters"
))
class JobOfferListView(generics.ListAPIView):
    serializer_class = JobOfferSerializer

    def get_queryset(self):
        serializer = JobOfferFiltersSerializer(data=self.request.data)
        if serializer.is_valid():
            job_offer_filters = serializer.create(serializer.validated_data)
            valid_filters = job_offer_filters.get_filters()
            return JobOffer.objects.filter(removed=False, **valid_filters)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class JobOfferInterestedUsersView(views.APIView):

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='integer')
        ],
        responses={
            '200': 'OK',
            '401': 'No authorization token',
            '403': 'No user or user is not default user',
            '404': "Offer not found",
        },
        operation_description="Create or update database object for CV generation.",
    )
    @permission_classes([IsAuthenticated & IsDefaultUser])
    def post(self, request, offer_id):
        try:
            user = DefaultAccount.objects.get(user_id=request.user.id)
            try:
                instance = JobOffer.objects.get(pk=offer_id)
                instance.interested_users.add(user)
                instance.save()
                return Response(status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response("Offer not found", status.HTTP_404_NOT_FOUND)
        except ObjectDoesNotExist:
            return Response("No user or user is not default user", status=status.HTTP_403_FORBIDDEN)

    @swagger_auto_schema(
        manual_parameters=[
            Parameter('offer_id', IN_PATH, type='integer')
        ],
        responses={
            '200': 'Interested users',
            '401': 'No authorization token',
            '403': 'No user or user is not employer or offer not belongs to employer',
            '404': "Offer not found",
        },
        operation_description="Create or update database object for CV generation.",
    )
    @permission_classes([IsAuthenticated & IsEmployer])
    def get(self, request, offer_id):
        try:
            instance = JobOffer.objects.get(pk=offer_id)
            is_employer = EmployerAccount.objects.filter(id=instance.employer_id, user_id=request.user.id).exists()
            if is_employer:
                serializer = InterestedUserSerializer(instance.interested_users, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response("Offer not belongs to employer", status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response("Offer not found", status.HTTP_404_NOT_FOUND)


@method_decorator(name='get', decorator=swagger_auto_schema(
    query_serializer=JobOfferFiltersSerializer,
    responses={
        '200': 'List of offers',
        '401': 'No authorization token',
        '403': 'No user or user is not employer',
        '404': "Bad request",
    },
    operation_description="Returns offers list with filters for current employer"
))
class EmployerJobOffersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated & IsEmployer]
    serializer_class = JobOfferSerializer

    def get_queryset(self):
        serializer = JobOfferFiltersSerializer(data=self.request.data)
        try:
            employer = EmployerAccount.objects.get(user_id=self.request.user.id)
            if serializer.is_valid():
                job_offer_filters = serializer.create(serializer.validated_data)
                valid_filters = job_offer_filters.get_filters()
                return JobOffer.objects.filter(removed=False, employer_id=employer.id, **valid_filters)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response("No user or user is not employer", status=status.HTTP_403_FORBIDDEN)
