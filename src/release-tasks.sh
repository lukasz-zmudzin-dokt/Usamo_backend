#!/bin/bash
python manage.py migrate
python manage.py loaddata test_account.json
python manage.py loaddata test_cv.json
python manage.py loaddata test_blog.json
python manage.py loaddata test_job.json
python manage.py loaddata test_videos.json