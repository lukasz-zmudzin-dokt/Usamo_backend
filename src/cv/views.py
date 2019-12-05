import os

from django.core.serializers import serialize
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

import json
import jinja2
import pdfkit
import subprocess
import io
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer

from cv.serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework import views

def index(request):
    return HttpResponse("Hello, world. You're at the CV generator.")


class GenerateView(views.APIView):
    @permission_classes([IsAuthenticated])
    def post(self, request):
        response_data = {}
        request_data = request.data
        request_data['cv_id'] = request.user.id
        serializer = CVSerializer(data=request_data)
        if serializer.is_valid():
            cv = serializer.create(serializer.validated_data)
            response = HttpResponse(generate(request_data), content_type='application/pdf')
            return response
        else:
            return Response(serializer.errors, status.HTTP_406_NOT_ACCEPTABLE)

    def get(self, request):
        try:
            cv = CV.objects.get(cv_id=request.user.id)
        except CV.DoesNotExist:
            return HttpResponse(status=404)
        serializer = CVSerializer(cv)
        return JsonResponse(serializer.data, safe=False)

def generate(data):
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
    pdf_2_path = os.path.join(module_dir, 'cv2.pdf')

    # get data and jinja
#    with io.open(file_path, "r", encoding="utf-8") as json_file:
#        data = json.load(json_file)
    env = jinja2.environment.Environment(
        loader=jinja2.FileSystemLoader(template_path)
    )
    template = env.get_template('template.tpl')

    # generate first html and pdf
    with io.open(cv_1_path, "w", encoding="utf-8") as f:
        f.write(template.render(**data))
    pdfkit.from_file(cv_1_path, pdf_1_path, configuration=_get_pdfkit_config())

    # generate second html and pdf
    template = env.get_template('template2.tpl')
    with io.open(cv_2_path, "w", encoding="utf-8") as f:
        f.write(template.render(**data))
    pdfkit.from_file(cv_2_path, pdf_2_path, configuration=_get_pdfkit_config(), options=options)

    # right now it returns the second pdf
    with open(pdf_2_path, 'rb') as f:
        d = f.read()
        response = HttpResponse(d, content_type='application/pdf')
        return response

    # return HttpResponse("CVs generated!")
    # return render(request, 'cv2-generated.html')


def _get_pdfkit_config():
    return pdfkit.configuration(wkhtmltopdf='./bin/wkhtmltopdf')