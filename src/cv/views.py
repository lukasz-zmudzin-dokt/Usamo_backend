
import os

from drf_yasg import openapi
from django.http import HttpResponse, JsonResponse
from django.utils.datastructures import MultiValueDictKeyError
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from usamo import settings
import jinja2
import pdfkit
import platform
import io
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas import ManualSchema

from cv.serializers import *
from rest_framework import status, generics, parsers, renderers
from rest_framework.response import Response
from rest_framework import views


def index(request):
    return HttpResponse("Hello, world. You're at the CV generator.")


class GenerateView(views.APIView):
    serializer_class = CVSerializer

    @swagger_auto_schema(
        request_body=CVSerializer,
        responses={
            '201': 'CV successfully generated.',
            '400': "Bad Request"
        },
        operation_description="Create or update database object for CV generation.",
    )
    def post(self, request):
        request_data = request.data
        request_data['cv_id'] = request.user.id
        serializer = self.serializer_class(data=request_data)
        if serializer.is_valid():
            cv = serializer.create(serializer.validated_data)
            return Response('CV successfully generated.', status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_406_NOT_ACCEPTABLE)

    @swagger_auto_schema(
        operation_description='Generate pdf url based on existing CV data.',
        responses={
            '200': 'url',
            '404': 'CV not found'
    }
    )
    def get(self, request):
        if request.user.is_staff:
            cv_id = request.data['cv_id']
        else:
            cv_id = request.user.id
        try:
            cv = CV.objects.get(cv_id=cv_id)
        except CV.DoesNotExist:
            return Response('CV not found', status.HTTP_404_NOT_FOUND)
        serializer = CVSerializer(cv)
        token = request.headers['Authorization'][6:]
        response = Response(generate(serializer.data, token, request.user.first_name, request.user.last_name), status.HTTP_200_OK)
        return response

    @swagger_auto_schema(
        operation_description="Deletes current user's pdf file from server if it exists",
        responses={
            '200': 'File deleted successfully',
            '404': 'No such file exists'
        }
    )
    def delete(self, request):
        module_dir = os.path.dirname(__file__)
        token = request.headers['Authorization'][6:]
        path = os.path.join(module_dir, f'{token}', f'CV_{request.user.first_name}_{request.user.last_name}.pdf')
        if os.path.isfile(path):
            os.remove(path)
            return Response('File deleted successfully', status.HTTP_200_OK)
        else:
            return Response('No such file exists', status.HTTP_404_NOT_FOUND)


class DataView(views.APIView):
    @swagger_auto_schema(
        operation_description="Returns current user's CV data in json format",
        responses={
            '200': CVSerializer,
            '404': 'CV not found'
        }
    )
    def get(self, request):
        try:
            cv = CV.objects.get(cv_id=request.user.id)
        except CV.DoesNotExist:
            return Response('CV not found', status.HTTP_404_NOT_FOUND)
        serializer = CVSerializer(instance=cv)
        return JsonResponse(serializer.data)


class PictureView(views.APIView):
    @swagger_auto_schema(
        operation_description="Posts picture to be used in user's CV",

        manual_parameters=[
            openapi.Parameter(
                in_='header',
                name='Content-Type',
                type=openapi.TYPE_STRING,
                default='application/x-www-form-urlencoded'
            ),
            openapi.Parameter(
                name='picture',
                in_='form-data',
                type=openapi.TYPE_FILE
            )],
        responses={
            '201': 'File added successfully.',
            '404': 'CV not found.',
            '406': 'Make sure the form key is "picture".'
        }
    )
    def post(self, request):
        user = request.user
        user_id = user.id
        try:
            cv = CV.objects.get(cv_id=request.user.id)
        except CV.DoesNotExist:
            return Response('CV not found.', status.HTTP_404_NOT_FOUND)
        serializer = CVSerializer(instance=cv)
        data = serializer.data
        try:
            pict = request.FILES['picture']
            ext = pict.name.split('.')[-1]
            pict.name = f'CV_{user.first_name}_{user.last_name}.' + ext
            data['basic_info']['picture'] = pict
        except MultiValueDictKeyError:
            Response('Make sure the form key is "picture".', status.HTTP_406_NOT_ACCEPTABLE)
        serializer = CVSerializer(data=data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return Response('File added successfully.', status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_406_NOT_ACCEPTABLE)

    @swagger_auto_schema(
        operation_description="Returns user's picture url if uploaded",
        responses={
            200:'url',
            404:'CV/picture not found'
        }
    )
    def get(self, request):
        try:
            cv = CV.objects.get(cv_id=request.user.id)
        except CV.DoesNotExist:
            return Response('CV not found.', status.HTTP_404_NOT_FOUND)
        bi = BasicInfo.objects.get(cv=cv)
        if not bi.picture:
            return Response('Picture not found.', status.HTTP_404_NOT_FOUND)
        return Response(bi.picture.url, status.HTTP_200_OK)


class UnverifiedCVList(generics.ListAPIView):
    """
    Returns a list of CVs whose owners want them to be
    verified and which haven't yet been verified.
    Requires admin privileges.
    """
    serializer_class = CVSerializer
    permission_classes = [IsAdminUser]
    def get_queryset(self):
        return CV.objects.filter(wants_verification=True, is_verified=False)


class AdminFeedback(generics.CreateAPIView):
    """
    Adds feedback from admin to an existing CV.
    Requires admin privileges.
    """
    permission_classes = [IsAdminUser]
    serializer_class = FeedbackSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UserFeedback(generics.RetrieveAPIView):
    """
    Returns current user's CV feedback from admin.
    """
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        fb = get_object_or_404(Feedback.objects.filter(cv_id=self.request.user.id))
        return fb


def generate(data, token, first_name, last_name):
    # options for second pdf
    options = {
        'page-size': 'Letter',
        'margin-top': '0in',
        'margin-right': '0in',
        'margin-bottom': '0in',
        'margin-left': '0in'
    }

    # get paths
    module_dir = os.path.dirname(__file__)  # get current directory
    file_path = os.path.join(module_dir, 'data_sample.json')
    template_path = os.path.join(module_dir, 'templates/')
    cv_1_path = os.path.join(module_dir, 'templates/cv1-generated.html')
    pdf_1_path = os.path.join(module_dir, 'cv1.pdf')
    cv_2_path = os.path.join(module_dir, 'templates/cv2-generated.html')
    pdf_2_path = os.path.join(f'{os.path.dirname(os.path.abspath(__file__))}',
                              f'{token}',
                              f'CV_{first_name}_{last_name}.pdf')
    if not os.path.exists(pdf_2_path):
        os.makedirs(os.path.join(f'{os.path.dirname(os.path.abspath(__file__))}',
                              f'{token}'))

    # get data and jinja
#    with io.open(file_path, "r", encoding="utf-8") as json_file:
#        data = json.load(json_file)
    env = jinja2.environment.Environment(
        loader=jinja2.FileSystemLoader(template_path)
    )
#    template = env.get_template('template.tpl')

    # generate first html and pdf
#    with io.open(cv_1_path, "w", encoding="utf-8") as f:
#        f.write(template.render(**data))
#    pdfkit.from_file(cv_1_path, pdf_1_path)

    # generate second html and pdf
    template = env.get_template('template2.tpl')
    with io.open(cv_2_path, "w", encoding="utf-8") as f:
        f.write(template.render(**data))
    if platform.system() == 'Windows':
        options['zoom'] = '0.78125'
    print(pdf_2_path)
    pdfkit.from_file(cv_2_path, pdf_2_path, configuration=settings._get_pdfkit_config(), options=options)
    # right now it returns the second pdf
    return pdf_2_path
    # return HttpResponse("CVs generated!")
    # return render(request, 'cv2-generated.html')
