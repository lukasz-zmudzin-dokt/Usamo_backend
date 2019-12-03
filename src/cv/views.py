from django.http import HttpResponse
from django.shortcuts import render

import json
import jinja2
import pdfkit
import os
import io
from cv.serializers import *
from rest_framework import status
from rest_framework.response import Response

def index(request):
    return HttpResponse("Hello, world. You're at the CV generator.")


def post(request):
    serializer = CVSerializer(data=request.data)
    response_data = {}

    if serializer.is_valid():
        cv = serializer.create(serializer.validated_data)
        response_data['response_message'] = "Successfully registered a new user"
        response_data['first_name'] = cv.user.first_name
        response_data['username'] = cv.user.username
    else:
        return Response(serializer.errors, status.HTTP_406_NOT_ACCEPTABLE)

    return Response(response_data, status=status.HTTP_201_CREATED)


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
    pdfkit.from_file(cv_1_path, pdf_1_path)

    # generate second html and pdf
    template = env.get_template('template2.tpl')
    with io.open(cv_2_path, "w", encoding="utf-8") as f:
        f.write(template.render(**data))
    pdfkit.from_file(cv_2_path, pdf_2_path, options=options)

    # right now it returns the second pdf
    with open(pdf_2_path, 'rb') as f:
        d = f.read()
        response = HttpResponse(d, content_type='application/pdf')
        return response

    # return HttpResponse("CVs generated!")
    # return render(request, 'cv2-generated.html')