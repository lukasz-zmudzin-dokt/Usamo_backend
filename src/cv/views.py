import sys

from django.http import HttpResponse, JsonResponse
import os

from django.core.serializers import serialize
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError

from usamo import settings

import json
import jinja2
import pdfkit
import subprocess
import platform
import io
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from cv.serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework import views


def index(request):
    return HttpResponse("Hello, world. You're at the CV generator.")


class GenerateView(views.APIView):
    @permission_classes([IsAuthenticated])
    def post(self, request):
        request_data = request.data
        request_data['cv_id'] = request.user.id
        serializer = CVSerializer(data=request_data)
        if serializer.is_valid():
            cv = serializer.create(serializer.validated_data)
            return Response('CV successfully generated.', status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_406_NOT_ACCEPTABLE)

    @permission_classes([IsAuthenticated])
    def get(self, request):
        try:
            cv = CV.objects.get(cv_id=request.user.id)
        except CV.DoesNotExist:
            return Response('CV not found', status.HTTP_404_NOT_FOUND)
        serializer = CVSerializer(cv)
        response = Response(generate(serializer.data, request.user.first_name, request.user.last_name), status.HTTP_200_OK)
        return response

    @permission_classes([IsAuthenticated])
    def delete(self, request):
        module_dir = os.path.dirname(__file__)
        path = os.path.join(module_dir, f'CV_{request.user.first_name}_{request.user.last_name}.pdf')
        if os.path.isfile(path):
            os.remove(path)
            return Response('File deleted successfully', status.HTTP_200_OK)
        else:
            return Response('No such file exists', status.HTTP_404_NOT_FOUND)


class DataView(views.APIView):
    @permission_classes([IsAuthenticated])
    def get(self, request):
        try:
            cv = CV.objects.get(cv_id=request.user.id)
        except CV.DoesNotExist:
            return Response('CV not found', status.HTTP_404_NOT_FOUND)
        serializer = CVSerializer(instance=cv)
        return JsonResponse(serializer.data)


class PictureView(views.APIView):
    @permission_classes([IsAuthenticated])
    def post(self, request):
        user_id = request.user.id
        cv = CV.objects.get(cv_id=user_id)
        serializer = CVSerializer(instance=cv)
        data = serializer.data
        try:
            pict = request.FILES['picture']
            ext = pict.name.split('.')[-1]
            pict.name = str(cv.id) + '.' + ext
            data['basic_info']['picture'] = pict
        except MultiValueDictKeyError:
            Response('Make sure the form key is "picture"', status.HTTP_406_NOT_ACCEPTABLE)
        serializer = CVSerializer(data=data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return Response('File added successfully', status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_406_NOT_ACCEPTABLE)

    @permission_classes([IsAuthenticated])
    def get(self, request):
        try:
            cv = CV.objects.get(cv_id=request.user.id)
        except CV.DoesNotExist:
            return Response('CV not found', status.HTTP_404_NOT_FOUND)
        picture = BasicInfo.objects.get(cv=cv).picture
        if picture is None:
            return Response('Picture not found', status.HTTP_404_NOT_FOUND)
        return Response(picture.url, status.HTTP_200_OK)
    
def generate(data, first_name, last_name):
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
    pdf_2_path = f'cv/CV_{first_name}_{last_name}.pdf'

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
    pdfkit.from_file(cv_2_path, pdf_2_path, configuration=settings._get_pdfkit_config(), options=options)
    # right now it returns the second pdf
    return pdf_2_path
    # return HttpResponse("CVs generated!")
    # return render(request, 'cv2-generated.html')
