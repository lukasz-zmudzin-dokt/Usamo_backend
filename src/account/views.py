from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework import views
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import permission_classes
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .filters import *
from .permissions import CanStaffVerifyUsers
from .serializers import *
from .models import *
from .filters import *
from .swagger import sample_default_account_request_schema, sample_employer_account_request_schema


class AbstractRegistrationView(views.APIView):
    permission_classes = [AllowAny]

    def perform_registration(self, serializer):
        response_data = {}
        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)
            self.set_response_params(user=user, response_data=response_data)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

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
    response = openapi.Schema(properties={
        'response_message': openapi.Schema(type='string', default='Successfully registered a new user'),
        'email': openapi.Schema(type='string', format='email', default='example@domain.com'),
        'username': openapi.Schema(type='string', default='sample_user'),
        'token': openapi.Schema(type='string', default='8f67f4a7e4c79f720ea82e6008f2f6e8a9661af7'),
        'status': openapi.Schema(type='string', default='Waiting for verification'),
        'type': openapi.Schema(type='string', default=account_type)
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
        request_body=sample_default_account_request_schema(),
        responses={
            201: sample_registration_response('Standard'),
            400: 'Serializer errors'
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
        request_body=sample_employer_account_request_schema(),
        responses={
            201: sample_registration_response('Employer'),
            400: 'Serializer errors'
        }
    )
    def post(self, request):
        serializer = EmployerAccountSerializer(data=request.data)
        return self.perform_registration(serializer=serializer)


class StaffRegistrationView(AbstractRegistrationView):

    permission_classes = [CanStaffVerifyUsers]

    @swagger_auto_schema(
        query_serializer=StaffAccountSerializer,
        responses={
            201: sample_registration_response('Staff'),
            400: 'Serializer errors'
        }
    )
    def post(self, request):
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
            201: 'Generated token and user type',
            400: 'Serializer errors/ Unable to login with given credentials'
        }
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
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class UserStatusView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Zwraca status aktualnie zalogowanego użytkownika",
        responses={
            200: 'is_verified: true/false'
        }
    )
    def get(self, request):
        verified = False
        if request.user.status == 1:
            verified = True

        response_data = {'is_verified': verified}
        return Response(response_data, status.HTTP_200_OK)


class DataView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get currently logged in user's data."
                              "Example response is for default user.",

        responses={
            200: DefaultAccountSerializer
        }
    )
    def get(self, request):
        serializer = None
        user_type = AccountType.STANDARD.value
        if request.user.type == AccountType.STANDARD.value:
            serializer = DefaultAccountDetailSerializer(instance=request.user)
        elif request.user.type == AccountType.EMPLOYER.value:
            serializer = EmployerDetailSerializer(instance=request.user)
            user_type = AccountType.EMPLOYER.value
        else:
            serializer = StaffDetailSerializer(instance=request.user)
            user_type = AccountType.STAFF.value

        return JsonResponse({'type': dict(ACCOUNT_TYPE_CHOICES)[user_type], 'data': serializer.data})


class AdminUserAdmissionView(views.APIView):
    permission_classes = [CanStaffVerifyUsers]

    @swagger_auto_schema(
        responses={
            '200': 'User successfully verified.',
            '400': 'User id was not specified.',
            '404': 'User with the id given was not found.'
        },
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_PATH, type='string($uuid)',
                              description='A UUID string identifying this account')
        ],
        operation_description="Sets user's status to verified.",
    )
    def post(self, request, user_id):
        if user_id is not None:
            try:
                user = Account.objects.get(pk=user_id)
            except Account.DoesNotExist:
                return Response('User with the id given was not found.', status.HTTP_404_NOT_FOUND)
            user.status = AccountStatus.VERIFIED.value
            user.save()
            return Response('User successfully verified.', status.HTTP_200_OK)

        return Response('User id was not specified.', status.HTTP_400_BAD_REQUEST)


class AdminUserRejectionView(views.APIView):
    permission_classes = [CanStaffVerifyUsers]

    @swagger_auto_schema(
        responses={
            '200': 'User status successfully set to not verified.',
            '400': 'User id was not specified.',
            '404': 'User with the id given was not found.'
        },
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_PATH, type='string($uuid)',
                              description='A UUID string identifying this account')
        ],
        operation_description="Sets user's status to not verified.",
    )
    def post(self, request, user_id):
        if user_id is not None:
            try:
                user = Account.objects.get(pk=user_id)
            except Account.DoesNotExist:
                return Response('User with the id given was not found.', status.HTTP_404_NOT_FOUND)
            user.status = AccountStatus.NOT_VERIFIED.value
            user.save()
            return Response('User status successfully set to not verified.', status.HTTP_200_OK)

        return Response('User id was not specified.', status.HTTP_400_BAD_REQUEST)


@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        '200': AccountListSerializer(many=True),
        '404': "Not found",
    },
    filter_inspectors=[DjangoFilterDescriptionInspector],
    operation_description="Returns all accounts list for admin"
))
class AdminAllAccountsListView(ListAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountListSerializer
    permission_classes = [CanStaffVerifyUsers]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserListFilter


@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        '200': AccountListSerializer(many=True),
        '404': "Not found",
    },
    filter_inspectors=[DjangoFilterDescriptionInspector],
    operation_description="Returns standard accounts list for admin"
))
class AdminDefaultAccountsListView(ListAPIView):
    serializer_class = AccountListSerializer
    permission_classes = [CanStaffVerifyUsers]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = DefaultAccountListFilter

    def get_queryset(self):
        return Account.objects.filter(type=AccountType.STANDARD.value)


@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        '200': AccountListSerializer(many=True),
        '404': "Not found",
    },
    filter_inspectors=[DjangoFilterDescriptionInspector],
    operation_description="Returns employer accounts list for admin"
))
class AdminEmployerListView(ListAPIView):
    serializer_class = AccountListSerializer
    permission_classes = [CanStaffVerifyUsers]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = EmployerListFilter

    def get_queryset(self):
        return Account.objects.filter(type=AccountType.EMPLOYER.value)


@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        '200': AccountListSerializer(many=True),
        '404': "Not found",
    },
    filter_inspectors=[DjangoFilterDescriptionInspector],
    operation_description="Returns staff accounts list for admin"
))
class AdminStaffListView(ListAPIView):
    serializer_class = AccountListSerializer
    permission_classes = [CanStaffVerifyUsers]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = StaffListFilter

    def get_queryset(self):
        return Account.objects.filter(type=AccountType.STAFF.value)


@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        '200': DefaultAccountDetailSerializer,
        '404': "Not found",
    },
    operation_description="Get user's data by specifying his/her id (for admin). Example response is for standard user."
))
class AdminUserDetailView(RetrieveAPIView):
    queryset = Account.objects.all()
    permission_classes = [CanStaffVerifyUsers]

    def get_serializer_class(self):
        pk = self.kwargs['pk']
        account = Account.objects.get(pk=pk)

        if account.type == AccountType.EMPLOYER.value:
            return EmployerDetailSerializer
        if account.type == AccountType.STAFF.value:
            return StaffDetailSerializer

        return DefaultAccountDetailSerializer
