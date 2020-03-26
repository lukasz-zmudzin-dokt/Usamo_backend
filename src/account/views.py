from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpRequest
from drf_yasg.openapi import Schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework import views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import permission_classes, api_view, renderer_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django_filters import rest_framework as filters

from .account_type import AccountType, ACCOUNT_TYPE_CHOICES
from .account_status import AccountStatus
from .serializers import *
from .models import *
from .filters import *


class AbstractRegistrationView(views.APIView):
    permission_classes = [AllowAny]

    def perform_registration(self, serializer):
        response_data = {}
        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)
            self.set_response_params(user=user, response_data=response_data)
        else:
            return Response(serializer.errors, status.HTTP_406_NOT_ACCEPTABLE)

        return Response(response_data, status=status.HTTP_201_CREATED)

    @staticmethod
    def set_response_params(user, response_data):
        response_data['response_message'] = "Successfully registered a new user"
        response_data['email'] = user.email
        response_data['username'] = user.username
        token = Token.objects.get(user=user).key
        response_data['token'] = token
        response_data['status'] = AccountStatus(user.status).name.lower()
        response_data['type'] = dict(ACCOUNT_TYPE_CHOICES)[user.type]


def sample_registration_response(account_type):
    response = Schema(properties={
        'response_message': Schema(type='string', default='Successfully registered a new user'),
        'email': Schema(type='string', format='email', default='example@domain.com'),
        'username': Schema(type='string', default='sample_user'),
        'token': Schema(type='string', default='8f67f4a7e4c79f720ea82e6008f2f6e8a9661af7'),
        'status': Schema(type='string', default='Waiting for verification'),
        'type': Schema(type='string', default=account_type)
    },
        type='object'
    )
    return response


class DefaultAccountRegistrationView(AbstractRegistrationView):
    """
    > ## Creates a default account
    > Required parameters:
    >
    > - username
    > - email
    > - password
    > - first_name
    > - last_name
    > - phone_number
    > - facility_name
    > - facility_address
    >
    """
    @swagger_auto_schema(
        query_serializer=DefaultAccountSerializer,
        responses={
            201: sample_registration_response('Standard'),
            406: 'Not acceptable'
        }
    )
    def post(self, request):
        serializer = DefaultAccountSerializer(data=request.data)
        return self.perform_registration(serializer=serializer)


class EmployerRegistrationView(AbstractRegistrationView):

    """
    > ## Creates an account for an employer
    > Required parameters:
    >
    > - username
    > - email
    > - password
    > - company_name
    > - company_address
    > - phone_number
    > - last_name
    > - first_name
    > - nip
    >
    """
    @swagger_auto_schema(
        query_serializer=EmployerAccountSerializer,
        responses={
            201: sample_registration_response('Employer'),
            406: 'Not acceptable'
        }
    )
    def post(self, request):
        serializer = EmployerAccountSerializer(data=request.data)
        return self.perform_registration(serializer=serializer)


class StaffRegistrationView(AbstractRegistrationView):
    @swagger_auto_schema(
        query_serializer=StaffAccountSerializer,
        responses={
            201: sample_registration_response('Staff'),
            406: 'Not acceptable'
        }
    )
    def post(self, request):
        print(request.data)
        serializer = StaffAccountSerializer(data=request.data)
        return self.perform_registration(serializer=serializer)


class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout currently logged in user.",
        responses={
            status.HTTP_200_OK: 'success: Successfully deleted the old token'
        }
    )
    def post(self, request):
        return self.logout(request)

    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        return Response({'success': 'Successfully deleted the old token'}, status.HTTP_200_OK)


class LoginView(ObtainAuthToken):

    @swagger_auto_schema(
        operation_description="Obtain auth token by specifying username and password",
        responses={
            status.HTTP_201_CREATED: 'Generated token and user type',
            status.HTTP_406_NOT_ACCEPTABLE: 'Serializer errors/ Unable to login with given credentials'}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'type': dict(ACCOUNT_TYPE_CHOICES)[user.type]
            }, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_406_NOT_ACCEPTABLE)


class DataView(views.APIView):

    @swagger_auto_schema(
        operation_description="Get currently logged in user's data."
                              "Example response is for default user.",

        responses={
            status.HTTP_200_OK: DefaultAccountSerializer}
    )
    @permission_classes([IsAuthenticated])
    def get(self, request):
        serializer = None
        user_type = AccountType.STANDARD.value
        if request.user.type == AccountType.STANDARD.value:
            serializer = DefaultAccountSerializer(instance=request.user)
        elif request.user.type == AccountType.EMPLOYER.value:
            serializer = EmployerAccountSerializer(instance=request.user)
            user_type = AccountType.EMPLOYER.value
        else:
            serializer = StaffAccountSerializer(instance=request.user)
            user_type = AccountType.STAFF.value

        return JsonResponse({'type': dict(ACCOUNT_TYPE_CHOICES)[user_type], 'data': serializer.data})


class AdminAllAccountsListView(ListAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountListSerializer
    permission_classes = [IsAdminUser]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserListFilter


class AdminDefaultAccountsListView(ListAPIView):
    serializer_class = AccountListSerializer
    permission_classes = [IsAdminUser]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = DefaultAccountListFilter

    def get_queryset(self):
        return Account.objects.filter(type=AccountType.STANDARD.value)


class AdminEmployerListView(ListAPIView):
    serializer_class = AccountListSerializer
    permission_classes = [IsAdminUser]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = EmployerListFilter

    def get_queryset(self):
        return Account.objects.filter(type=AccountType.EMPLOYER.value)


class AdminStaffListView(ListAPIView):
    serializer_class = AccountListSerializer
    permission_classes = [IsAdminUser]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = StaffListFilter

    def get_queryset(self):
        return Account.objects.filter(type=AccountType.STAFF.value)


class AdminUserDetailView(RetrieveAPIView):
    queryset = Account.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        pk = self.kwargs['pk']
        account = Account.objects.get(pk=pk)

        if account.type == AccountType.EMPLOYER.value:
            return EmployerDetailSerializer
        if account.type == AccountType.STAFF.value:
            return StaffDetailSerializer

        return DefaultAccountDetailSerializer
