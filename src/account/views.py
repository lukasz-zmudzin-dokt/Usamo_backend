from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status
from rest_framework import views
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .account_type import AccountType, ACCOUNT_TYPE_CHOICES
from .account_status import AccountStatus
from .serializers import DefaultAccountSerializer, EmployerAccountSerializer, StaffAccountSerializer


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

    def post(self, request):
        serializer = EmployerAccountSerializer(data=request.data)
        return self.perform_registration(serializer=serializer)


class StaffRegistrationView(AbstractRegistrationView):

    def post(self, request):
        serializer = StaffAccountSerializer(data=request.data)
        return self.perform_registration(serializer=serializer)


class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return self.logout(request)

    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        return Response({'success': 'Successfully deleted the old token'}, status.HTTP_200_OK)


class DataView(views.APIView):

    @permission_classes([IsAuthenticated])
    def get(self, request):
        serializer = None
        user_type = AccountType.STANDARD.value
        if request.user.type == AccountType.STANDARD.value:
            serializer = DefaultAccountSerializer(instance=request.user)
        elif request.user_type == AccountType.EMPLOYER.value:
            serializer = EmployerAccountSerializer(instance=request.user)
            user_type = AccountType.EMPLOYER.value
        else:
            serializer = StaffAccountSerializer(instance=request.user)
            user_type = AccountType.STAFF.value

        return JsonResponse({'type': dict(ACCOUNT_TYPE_CHOICES)[user_type], 'data': serializer.data})
