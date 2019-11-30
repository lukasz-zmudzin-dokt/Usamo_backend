from rest_framework import status
from rest_framework.response import Response
from rest_framework import views
from .serializers import UserSerializer
from .account_status import AccountStatus


# Create your views here.

class RegistationView(views.APIView):
    """
    Required parameters: first_name, last_name, email, username, password, confirmed_password, phone_number
    """

    def post(self, request):

        serializer = UserSerializer(data=request.data)
        response_data = {}

        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)
            response_data['response_message'] = "Successfully registered a new user"
            response_data['email'] = user.email
            response_data['username'] = user.username
            response_data['status'] = AccountStatus(user.account.status).name.lower()
        else:
            return Response(serializer.errors, status.HTTP_406_NOT_ACCEPTABLE)

        return Response(response_data, status=status.HTTP_201_CREATED)
