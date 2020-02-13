from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status
from rest_framework import views
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .account_status import AccountStatus
from .serializers import UserSerializer, EmployerSerializer


# Create your views here.


class BasicRegistrationView(views.APIView):
    permission_classes = [AllowAny]

    def perform_registration(self, serializer):
        response_data = {}
        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)
            self.set_response_params(user=user, response_data=response_data)
        else:
            return Response(serializer.errors, status.HTTP_406_NOT_ACCEPTABLE)

        return Response(response_data, status=status.HTTP_201_CREATED)

    def set_response_params(self, user, response_data):
        response_data['response_message'] = "Successfully registered a new user"
        response_data['email'] = user.email
        response_data['username'] = user.username
        token = Token.objects.get(user=user).key
        response_data['token'] = token
        response_data['status'] = AccountStatus(user.status).name.lower()


class RegistrationView(BasicRegistrationView):
    """
    Required parameters: first_name, last_name, email,
    username, password, phone_number, facility_name,
    facility_address
    """
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        return self.perform_registration(serializer=serializer, )


class EmployerRegistrationView(BasicRegistrationView):

    def post(self, request):
        serializer = EmployerSerializer(data=request.data)
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
        serializer = UserSerializer(instance=request.user)
        return JsonResponse(serializer.data)
