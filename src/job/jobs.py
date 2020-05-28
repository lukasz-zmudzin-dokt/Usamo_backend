import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")
scheduler.start()


def delete_zip_file(path):
    if os.path.isfile(path):
        os.remove(path)


def delete_zip_file_after_delay(path):
    scheduler.add_job(delete_zip_file, 'date', [path], run_date=datetime.now() + timedelta(minutes=10))
