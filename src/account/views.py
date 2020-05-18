from django.contrib.auth import login
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from knox.views import LoginView as KnoxLoginView
from knox.views import LogoutView as KnoxLogoutView
from knox.views import LogoutAllView as KnoxLogoutAllView
from rest_framework import status
from rest_framework import views
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import CanStaffVerifyUsers, IsStaffMember
from .serializers import *
from .models import *
from .filters import *
from .swagger import sample_default_account_request_schema, sample_employer_account_request_schema, sample_registration_response, sample_login_response
from rest_framework.pagination import PageNumberPagination
from job.views import ErrorResponse, MessageResponse


class UserListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class AbstractRegistrationView(KnoxLoginView):
    permission_classes = [AllowAny]

    def perform_registration(self, serializer, request):
        response_data = {}
        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)
            self.set_response_params(user=user, response_data=response_data)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        token_data = self.__create_token(request)
        response_data['token_data'] = token_data
        return Response(response_data, status.HTTP_201_CREATED)

    def __create_token(self, request):
        token_serializer = AuthTokenSerializer(data=request.data)
        token_serializer.is_valid(raise_exception=True)
        user = token_serializer.validated_data['user']
        login(request, user)
        return super(AbstractRegistrationView, self).post(request, format=None).data

    @staticmethod
    def set_response_params(user, response_data):
        response_data['message'] = "Rejestracja powiodła się"
        response_data['email'] = user.email
        response_data['username'] = user.username
        response_data['status'] = AccountStatus(user.status).name.lower()
        response_data['type'] = dict(ACCOUNT_TYPE_CHOICES)[user.type]


class DefaultAccountRegistrationView(AbstractRegistrationView):
    operation_description = "Rejestruje standardowego użytkownika",
    @swagger_auto_schema(
        request_body=sample_default_account_request_schema(),
        responses={
            201: sample_registration_response('standard'),
            400: 'Błędy walidacji (np. brakujące pole)'
        }
    )
    def post(self, request):
        serializer = DefaultAccountSerializer(data=request.data)
        return self.perform_registration(serializer, request)


class EmployerRegistrationView(AbstractRegistrationView):
    operation_description = "Rejestruje konto pracodawcy",
    @swagger_auto_schema(
        request_body=sample_employer_account_request_schema(),
        responses={
            201: sample_registration_response('employer'),
            400: 'Błędy walidacji (np. brakujące pole)'
        }
    )
    def post(self, request):
        serializer = EmployerAccountSerializer(data=request.data)
        return self.perform_registration(serializer, request)


class StaffRegistrationView(AbstractRegistrationView):
    permission_classes = [CanStaffVerifyUsers]

    @swagger_auto_schema(
        operation_description="Rejestruje użytkownika z personelu. Wymaga odpowiednich uprawnień",
        query_serializer=StaffAccountSerializer,
        responses={
            201: sample_registration_response('staff'),
            400: 'Błędy walidacji (np. brakujące pole)'
        }
    )
    def post(self, request):
        serializer = StaffAccountSerializer(data=request.data)
        return self.perform_registration(serializer, request)


class LogoutView(KnoxLogoutView):

    @swagger_auto_schema(
        operation_description="Wylogowuje aktualnego użytkownika na obecnym urządzeniu",
        responses={
            status.HTTP_200_OK: 'message: Wylogowano pomyślnie'
        }
    )
    def post(self, request):
        response = super(LogoutView, self).post(request)
        return Response({'message': 'Wylogowano pomyślnie'},
                        status.HTTP_200_OK) if response.data is None else response


class LogoutAllView(KnoxLogoutAllView):

    @swagger_auto_schema(
        operation_description="Wylogowuje użytkownika ze wszystkich urządzeń",
        responses={
            status.HTTP_200_OK: 'message: Pomyślnie wylogowano ze wszystkich urządzeń'
        }
    )
    def post(self, request, format=None):
        super(LogoutAllView, self).post(request)
        return Response({'message': 'Pomyślnie wylogowano ze wszystkich urządzeń'})


class LoginView(KnoxLoginView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Zwraca token, jego datę ważności oraz typ użytkownika w oparciu o "
                              "username i hasło",
        responses={
            200: sample_login_response(AccountType.STANDARD.value),
            400: 'Błędy walidacji (np. brakujące pole) '
                 '/ Podane dane uwierzytelniające nie pozwalają na zalogowanie.'
        }
    )
    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        response = super(LoginView, self).post(request, format=None)
        response.data['type'] = dict(ACCOUNT_TYPE_CHOICES)[user.type]
        return response


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
        operation_description="Zwraca dane aktualnego użytkownika. "
                              "Przykład jest dla użytkownika standardowego",

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
            '200': 'Użytkownik został pomyślnie zweryfikowany',
            '400': 'Nie podano id użytkownika',
            '404': 'Nie znaleziono użytkownika'
        },
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_PATH, type='string($uuid)',
                              description='A UUID string identifying this account')
        ],
        operation_description="Ustawia status użytkownika na zweryfikowany",
    )
    def post(self, request, user_id):
        if user_id is not None:
            try:
                user = Account.objects.get(pk=user_id)
            except Account.DoesNotExist:
                return ErrorResponse('Nie znaleziono użytkownika', status.HTTP_404_NOT_FOUND)
            user.status = AccountStatus.VERIFIED.value
            user.save()
            return MessageResponse('Użytkownik został pomyślnie zweryfikowany')

        return ErrorResponse('Nie podano id użytkownika', status.HTTP_400_BAD_REQUEST)


class AdminUserRejectionView(views.APIView):
    permission_classes = [CanStaffVerifyUsers]

    @swagger_auto_schema(
        responses={
            '200': 'message: Użytkownik został pomyślnie odrzucony',
            '400': 'error: ID użytkownika nie zostało podane',
            '404': 'error: Użytkownik o podanym id nie został znaleziony.'
        },
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_PATH, type='string($uuid)',
                              description='String UUID będący id danego użytkownika')
        ],
        operation_description="Ustawia status użytkownika na rejected.",
    )
    def post(self, request, user_id):
        if user_id is not None:
            try:
                user = Account.objects.get(pk=user_id)
            except Account.DoesNotExist:
                return ErrorResponse('Użytkownik o podanym ID nie został znaleziony', status.HTTP_404_NOT_FOUND)
            user.status = AccountStatus.REJECTED.value
            user.save()
            return MessageResponse('Użytkownik został pomyślnie odrzucony')

        return ErrorResponse('ID użytkownika nie zostało podane', status.HTTP_400_BAD_REQUEST)


class AdminUserBlockView(views.APIView):
    permission_classes = [CanStaffVerifyUsers]

    @swagger_auto_schema(
        responses={
            '200': 'message: Użytkownik został pomyślnie zablokowany',
            '400': 'error: ID użytkownika nie zostało podane',
            '404': 'error: Użytkownik o podanym ID nie został znaleziony'
        },
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_PATH, type='string($uuid)',
                              description='String UUID będący id danego użytkownika')
        ],
        operation_description="Ustawia status użytkownika na blocked.",
    )
    def post(self, request, user_id):
        if user_id is not None:
            try:
                user = Account.objects.get(pk=user_id)
            except Account.DoesNotExist:
                return ErrorResponse('Użytkownik o podanym ID nie został znaleziony', status.HTTP_404_NOT_FOUND)
            user.status = AccountStatus.BLOCKED.value
            user.save()
            return MessageResponse('Użytkownik został pomyślnie zablokowany')

        return ErrorResponse('ID użytkownika nie zostało podane', status.HTTP_400_BAD_REQUEST)


@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[DjangoFilterDescriptionInspector],
    operation_description="Zwraca listę wszystkich użytkowników dla admina"
))
class AdminAllAccountsListView(ListAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountListSerializer
    permission_classes = [IsStaffMember]
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filterset_class = UserListFilter
    ordering_fields = ['username', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    pagination_class = UserListPagination


@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[DjangoFilterDescriptionInspector],
    operation_description="Zwrca listę standardowych użytkowników dla admina"
))
class AdminDefaultAccountsListView(ListAPIView):
    serializer_class = AccountListSerializer
    permission_classes = [IsStaffMember]
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filterset_class = DefaultAccountListFilter
    ordering_fields = ['username', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    pagination_class = UserListPagination

    def get_queryset(self):
        return Account.objects.filter(type=AccountType.STANDARD.value)


@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[DjangoFilterDescriptionInspector],
    operation_description="Zwraca listę kont pracodawców dla admina"
))
class AdminEmployerListView(ListAPIView):
    serializer_class = AccountListSerializer
    permission_classes = [IsStaffMember]
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filterset_class = EmployerListFilter
    ordering_fields = ['username', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    pagination_class = UserListPagination

    def get_queryset(self):
        return Account.objects.filter(type=AccountType.EMPLOYER.value)


@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[DjangoFilterDescriptionInspector],
    operation_description="Zwrca listę kont personelu dla admina"
))
class AdminStaffListView(ListAPIView):
    serializer_class = AccountListSerializer
    permission_classes = [IsStaffMember]
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filterset_class = StaffListFilter
    ordering_fields = ['username', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    pagination_class = UserListPagination

    def get_queryset(self):
        return Account.objects.filter(type=AccountType.STAFF.value)


@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        '200': DefaultAccountDetailSerializer,
        '404': "Not found",
    },
    operation_description="Zwraca dane użytkownika w oparciu o jego id dla admina."
                          " Przykład jest dla użytkownika standardowego"
))
class AdminUserDetailView(RetrieveAPIView):
    queryset = Account.objects.all()
    permission_classes = [IsStaffMember]

    def get_serializer_class(self):
        pk = self.kwargs['pk']
        account = Account.objects.get(pk=pk)

        if account.type == AccountType.EMPLOYER.value:
            return EmployerDetailSerializer
        if account.type == AccountType.STAFF.value:
            return StaffDetailSerializer

        return DefaultAccountDetailSerializer


class AccountEditView(views.APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            account = Account.objects.get(pk=request.user.id)
            try:
                new_password = request.data['password']
            except KeyError:
                return Response("Key 'password' is not defined in JSON request")
            account.set_password(new_password)
            account.save()
            return Response("User data updated", status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response("User not found in database", status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        try:
            account = Account.objects.get(pk = request.user.id)
            account.delete()
            return Response("Account successfully deleted", status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response("User not found in database", status.HTTP_404_NOT_FOUND)


class AdminAccountEditView(views.APIView):
    permission_classes = [CanStaffVerifyUsers]

    def put(self, request, user_id):
        if user_id is not None:
            try:
                account = Account.objects.get(pk=user_id)
            except Account.DoesNotExist:
                return Response('User with the id given was not found.', status.HTTP_404_NOT_FOUND)
        if account.type == AccountType.STANDARD.value:
            serializer = DefaultAccountSerializer(account, data=request.data, partial=True)
        elif account.type == AccountType.EMPLOYER.value:
            serializer = EmployerAccountSerializer(account, data=request.data, partial=True)
        elif account.type == AccountType.STAFF.value:
            serializer = StaffAccountSerializer(account, data=request.data, partial=True)
        else:
            return Response("User not found", status.HTTP_404_NOT_FOUND)

        if serializer.is_valid():
            serializer.update(account, serializer.validated_data)
            return Response("Account data successfully updated", status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        try:
            account = Account.objects.get(pk=user_id)
            account.delete()
            return Response("Account successfully deleted", status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response("User not found in database", status.HTTP_404_NOT_FOUND)