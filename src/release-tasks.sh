#!/bin/bash
python manage.py migrate
python manage.py loaddata test_accounts.json
python manage.py loaddata test_cv.json
python manage.py loaddata test_blogs.json
python manage.py loaddata test_job.json