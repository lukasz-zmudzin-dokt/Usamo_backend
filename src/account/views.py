from rest_framework import status
from rest_framework.response import Response
from rest_framework import views
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer
from .account_status import AccountStatus
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.

class RegistationView(views.APIView):
    """
    Required parameters: first_name, last_name, email, username, password, confirmed_password, phone_number
    """
    permission_classes = [AllowAny]
    def post(self, request):

        serializer = UserSerializer(data=request.data)
        response_data = {}

        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)
            response_data['response_message'] = "Successfully registered a new user"
            response_data['email'] = user.email
            response_data['username'] = user.username
            response_data['status'] = AccountStatus(user.account.status).name.lower()
            token = Token.objects.get(user=user).key
            response_data['token'] = token
        else:
            return Response(serializer.errors, status.HTTP_406_NOT_ACCEPTABLE)

        return Response(response_data, status=status.HTTP_201_CREATED)


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
