from django.contrib.auth import login
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from knox.views import LoginView as KnoxLoginView
from knox.views import LogoutView as KnoxLogoutView
from knox.views import LogoutAllView as KnoxLogoutAllView
from django_apscheduler.models import DjangoJob
from notifications.signals import notify
from rest_framework import status
from rest_framework import views
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from notification.jobs import send_verification_email, send_account_data_change_email, send_rejection_email
from .permissions import *
from blog.permissions import IsStaffBlogModerator
from .serializers import *
from .models import *
from .filters import *
from .swagger import sample_default_account_request_schema, sample_employer_account_request_schema, sample_registration_response, sample_login_response, get_delete_picture_decorator, get_post_picture_decorator
from .swagger import *
from rest_framework.pagination import PageNumberPagination
from job.views import ErrorResponse, MessageResponse, sample_error_response, sample_message_response
from django.contrib.auth.hashers import check_password


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
        if isinstance(serializer, (DefaultAccountSerializer, EmployerAccountSerializer)):
            notify.send(user, recipient=Account.objects.filter(groups__name__contains='staff_verification'),
                        verb=f'Założono nowe konto do weryfikacji: {user.username}',
                        app='userApproval',
                        object_id=None
                        )
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


class UserDataView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self, request):
        if request.user.type == AccountType.STANDARD.value:
            serializer = DefaultAccountDetailSerializer(instance=request.user)
            user_type = AccountType.STANDARD.value
        elif request.user.type == AccountType.EMPLOYER.value:
            serializer = EmployerDetailSerializer(instance=request.user)
            user_type = AccountType.EMPLOYER.value
        else:
            serializer = StaffDetailSerializer(instance=request.user)
            user_type = AccountType.STAFF.value

        return serializer, user_type

    @swagger_auto_schema(
        operation_description="Zwraca dane aktualnego użytkownika. "
                              "Przykład jest dla użytkownika standardowego",
        responses={
            200: DefaultAccountSerializer
        }
    )
    def get(self, request):
        serializer, user_type = self.get_serializer_class(request)
        data = serializer.data
        user_id = str(request.user.id)
        data['is_subscribed'] = DjangoJob.objects.filter(name=user_id).exists()
        return JsonResponse({'type': dict(ACCOUNT_TYPE_CHOICES)[user_type], 'data': data})

    @swagger_auto_schema(
        responses={
            '200': sample_message_response("Konto zostało pomyślnie usunięte")
        },
        operation_description="Api pozwalające użytkownikowi usunąć swoje konto",
    )
    def delete(self, request):
        account = request.user
        account.delete()
        return MessageResponse("Konto zostało pomyślnie usunięte")


class PasswordChangeView(views.APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        responses={
            '200': sample_message_response("Hasło zostało zmienione"),
            '400': "Błędy walidacji",
            '403': sample_error_response("Stare hasło jest niepoprawne")
        },
        request_body=PasswordChangeRequestSerializer,
        operation_description="Api pozwalające użytkownikowi zmienić swoje hasło",
    )
    def patch(self, request):
        account = request.user
        serializer = PasswordChangeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_pass = request.data['old_password']
        new_pass = request.data['new_password']
        if check_password(old_pass, account.password):
            account.set_password(new_pass)
            account.save()
            account.auth_token_set.all().delete()
            return MessageResponse("Hasło zostało zmienione")
        return ErrorResponse("Stare hasło jest niepoprawne", status.HTTP_403_FORBIDDEN)


class StaffDataChangeView(views.APIView):
    permission_classes = (IsStaffMember, )

    @swagger_auto_schema(
        responses={
            '200': sample_message_response("Dane zostały pomyślnie zmienione"),
            '400': "Błędy walidacji"
        },
        request_body=StaffAccountSerializer,
        operation_description="Api pozwalające pracownikowi zmienić swoje dane (do hasła jest inne api). Uprawnień nie można zmieniać",
    )
    def patch(self, request):
        account = request.user
        serializer = StaffAccountSerializer(account, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.update(account, serializer.validated_data)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        return MessageResponse("Dane zostały pomyślnie zmienione")
       

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
            send_verification_email(user_id)
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

            if user.type == AccountType.STAFF.value:
                return ErrorResponse('Nie możesz usunąć tego użytkownika', status.HTTP_403_FORBIDDEN)

            user.status = AccountStatus.REJECTED.value
            user.save()
            send_rejection_email(user_id)
            return MessageResponse('Użytkownik został pomyślnie odrzucony')

        return ErrorResponse('ID użytkownika nie zostało podane', status.HTTP_400_BAD_REQUEST)


class AdminUserBlockView(views.APIView):
    permission_classes = (CanStaffVerifyUsers | IsStaffBlogModerator, )

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

            if user.type == AccountType.STAFF.value:
                return ErrorResponse('Nie możesz zablokować tego użytkownika', status.HTTP_403_FORBIDDEN)

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
    filter_backends = (DjangoFilterBackend, UserListOrderingFilter,)
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
    filter_backends = (DjangoFilterBackend, UserListOrderingFilter,)
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
    filter_backends = (DjangoFilterBackend, UserListOrderingFilter,)
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
    filter_backends = (DjangoFilterBackend, UserListOrderingFilter,)
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


class AdminUserDataEditView(views.APIView):
    permission_classes = [CanStaffVerifyUsers]

    @swagger_auto_schema(
        responses={
            '200': sample_message_response("Dane konta zostały zaktualizowane"),
            '400': "Błędy walidacji",
            '403': sample_error_response("Nie możesz edytować danych tego użytkownika"),
            '404': sample_error_response('Użytkownik o podanym id nie został znaleziony')
        },
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, type='string($uuid)',
                              description='String UUID będący id danego użytkownika')
        ],
        operation_description="Api dla admina do edycji danych użytkowników (w tym hasła).",
    )
    def patch(self, request, pk):
        try:
            account = Account.objects.get(pk=pk)
        except Account.DoesNotExist:
            return ErrorResponse('Użytkownik o podanym id nie został znaleziony', status.HTTP_404_NOT_FOUND)
        if account.type == AccountType.STANDARD.value:
            serializer = DefaultAccountSerializer(account, data=request.data, partial=True)
        elif account.type == AccountType.EMPLOYER.value:
            serializer = EmployerAccountSerializer(account, data=request.data, partial=True)
        elif account.type == AccountType.STAFF.value:
            return ErrorResponse("Nie możesz edytować danych tego użytkownika", status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.update(account, serializer.validated_data)
            send_account_data_change_email(pk, request.data)
            return MessageResponse("Dane konta zostały zaktualizowane")
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses={
            '200': sample_message_response("Konto zostało usunięte"),
            '403': sample_error_response("Nie możesz wykonać tej operacji"),
            '404': sample_error_response("Użytkownik o podanym id nie został znaleziony")
        },
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, type='string($uuid)',
                              description='String UUID będący id danego użytkownika')
        ],
        operation_description="Api dla admina do kasowania użytkowników. Nie można przez nie usuwać staffów.",
    )
    def delete(self, request, pk):
        try:
            account = Account.objects.get(pk=pk)
            if account.type == AccountType.STAFF.value:
                return ErrorResponse("Nie możesz wykonać tej operacji", status.HTTP_403_FORBIDDEN)
            account.delete()
            return MessageResponse("Konto zostało usunięte")
        except Account.DoesNotExist:
            return ErrorResponse("Użytkownik o podanym id nie został znaleziony", status.HTTP_404_NOT_FOUND)


class ProfilePictureView(views.APIView):

    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, )

    @method_decorator(name='post', decorator=get_post_picture_decorator())
    def post(self, request):
        serializer = ProfilePictureSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response({'picture_url': request.user.picture_url}, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @method_decorator(name='delete', decorator=get_delete_picture_decorator())
    def delete(self, request):
        user = request.user
        had_picture = user.delete_image_if_exists()
        if had_picture:
            return Response({'message': 'Pomyślnie usunięto zdjęcie'}, status.HTTP_200_OK)
        return Response({'message': 'Użytkownik nie ma zdjęcia'}, status.HTTP_404_NOT_FOUND)
