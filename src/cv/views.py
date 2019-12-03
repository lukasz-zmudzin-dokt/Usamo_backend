from django.http import HttpResponse
from django.shortcuts import render

import json
import jinja2
import pdfkit
import os
import io

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
    cv_1_path = os.path.join(module_dir, 'cv1.html')
    pdf_1_path = os.path.join(module_dir, 'cv1.pdf')
    cv_2_path = os.path.join(module_dir, 'cv2.html')
    pdf_2_path = os.path.join(module_dir, 'cv2.pdf')

    with io.open(file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    env = jinja2.environment.Environment(
        loader=jinja2.FileSystemLoader(template_path)
    )
    template = env.get_template('template.tpl')
    with io.open(cv_1_path, "w", encoding="utf-8") as f:
        f.write(template.render(**data))
    # TODO: install wkhtmltopdf
    pdfkit.from_file(cv_1_path, pdf_1_path)

    template = env.get_template('template2.tpl')
    with io.open(cv_2_path, "w", encoding="utf-8") as f:
        f.write(template.render(**data))
    pdfkit.from_file(cv_2_path, pdf_2_path, options=options)

    return HttpResponse("CVs generated!")
    #return render(request, 'cv/cv2.html')