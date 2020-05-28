from apscheduler.schedulers.background import BackgroundScheduler
from python_http_client import ForbiddenError
from sendgrid.helpers.mail import Mail, PlainTextContent
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from datetime import datetime, timedelta, timezone
from account.models import Account
from account.utils import send_mail_via_sendgrid
from django.conf import settings

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")
scheduler.start()


def send_notification_email(pk):
    user = Account.objects.get(id=pk)
    email = user.email
    notifications = user.notifications.filter(timestamp__gte=datetime.now().astimezone(timezone.utc) - timedelta(days=1))
    if notifications.count() > 0:
        verbs = [notification.verb for notification in notifications]
        times = [notification.timestamp.strftime('%d/%m/%y %H:%M') for notification in notifications]
        subject = f'Nowe powiadomienia z serwisu Usamodzielnieni ({notifications.count()})'
        content = 'Oto powiadomienia z serwisu Usamodzielnieni z ostatnich 24 godzin:\n'
        for verb, time in zip(verbs, times):
            content += str(verb) + ' | ' + str(time) + '\n'

        message = Mail(
            from_email='no-reply@usamodzielnieni.pl',
            to_emails=email,
            subject=subject,
            plain_text_content=PlainTextContent(content))
        try:
            send_mail_via_sendgrid(message)
        except ForbiddenError:
            pass


def start_scheduler(pk):
    scheduler.add_job(send_notification_email, 'cron', [pk], hour='6', replace_existing=True, id=str(pk))
    register_events(scheduler)


def stop_scheduler(pk):
    scheduler.remove_job(str(pk))


def send_verification_email(pk):
    user = Account.objects.get(id=pk)
    email = user.email
    login_url = settings.FRONT_URL + 'login'
    subject = f'Twoje konto w serwisie Usamodzielnieni zostało zweryfikowane!'
    content = f'Dzień dobry, {user.first_name}!\nZ przyjemnością informujemy, że Twoje konto {user.username} w ' \
              f'serwisie Usamodzielnieni zostało pomyślnie zweryfikowane. Możesz teraz zalogować się i korzystać ' \
              f'ze wszystkich dostępnych funkcji:\n{login_url}\nŻyczymy miłego dnia,\nZespół Usamodzielnionych'
    message = Mail(
        from_email='no-reply@usamodzielnieni.pl',
        to_emails=email,
        subject=subject,
        plain_text_content=PlainTextContent(content))
    try:
        send_mail_via_sendgrid(message)
    except ForbiddenError:
        pass
