from django.http import HttpResponse
from django.shortcuts import render

import json
import jinja2
import pdfkit
import os


def index(request):
    return HttpResponse("Hello, world. You're at the CV generator.")


def generate(request):
    options = {
        'page-size': 'Letter',
        'margin-top': '0in',
        'margin-right': '0in',
        'margin-bottom': '0in',
        'margin-left': '0in'
    }
    module_dir = os.path.dirname(__file__)  # get current directory
    file_path = os.path.join(module_dir, 'data.json')
    template_path = os.path.join(module_dir, 'templates/')
    cv_1_path = os.path.join(module_dir, 'templates/cv/cv1.html')
    cv_2_path = os.path.join(module_dir, 'templates/cv/cv2.html')

    with open(file_path) as json_file:
        data = json.load(json_file)

    env = jinja2.environment.Environment(
        loader=jinja2.FileSystemLoader(template_path)
    )
    template = env.get_template('template.tpl')
    with open(cv_1_path, "w") as f:
        f.write(template.render(**data))
    # TODO: install wkhtmltopdf
    # pdfkit.from_file('basic-cv.html', 'basic-cv.pdf')

    template = env.get_template('template2.tpl')
    with open(cv_2_path, "w") as f:
        f.write(template.render(**data))
    # pdfkit.from_file('basic-cv2.html', 'basic-cv2.pdf', options=options)

    #return HttpResponse("CVs generated!")
    return render(request, 'cv/cv2.html')