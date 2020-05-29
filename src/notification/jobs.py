from apscheduler.schedulers.background import BackgroundScheduler
from notifications.signals import notify
from python_http_client import ForbiddenError
from sendgrid.helpers.mail import Mail, PlainTextContent
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from datetime import timedelta
from django.utils import timezone
from account.models import Account
from account.utils import send_mail_via_sendgrid
from django.conf import settings
from job.models import JobOffer

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")
scheduler.start()


def start_scheduler(pk):
    scheduler.add_job(send_notification_email, 'cron', [pk], hour='6', replace_existing=True, id=str(pk))


def stop_scheduler(pk):
    scheduler.remove_job(str(pk))


def archive_old_job_offers():
    old_job_offers = JobOffer.objects.filter(expiration_date__lt=timezone.now())\
        .select_related('employer__user')
    for offer in old_job_offers:
        offer.removed = True
        offer.save()
        notify.send(offer.employer.user, recipient=offer.employer.user,
                    verb=f'Twoja oferta pracy {offer.offer_name} została zarchiwizowana',
                    app='myOffers',
                    object_id=None
                    )


scheduler.add_job(archive_old_job_offers, 'cron', hour='0', replace_existing=True, id='archive_old_job_offers_task')


def send_email(email, subject, content):
    message = Mail(
        from_email='no-reply@usamodzielnieni.pl',
        to_emails=email,
        subject=subject,
        plain_text_content=PlainTextContent(content))
    try:
        send_mail_via_sendgrid(message)
    except ForbiddenError:
        pass


def send_notification_email(pk):
    user = Account.objects.get(id=pk)
    email = user.email
    notifications = user.notifications.filter(timestamp__gte=timezone.now() - timedelta(days=1))
    if notifications.count() > 0:
        verbs = [notification.verb for notification in notifications]
        times = [notification.timestamp.strftime('%d/%m/%y %H:%M') for notification in notifications]
        subject = f'Nowe powiadomienia z serwisu Usamodzielnieni ({notifications.count()})'
        content = 'Oto powiadomienia z serwisu Usamodzielnieni z ostatnich 24 godzin:\n'
        for verb, time in zip(verbs, times):
            content += str(verb) + ' | ' + str(time) + '\n'
        send_email(email, subject, content)


def send_verification_email(pk):
    user = Account.objects.get(id=pk)
    email = user.email
    login_url = settings.FRONT_URL + 'login'
    subject = f'Twoje konto w serwisie Usamodzielnieni zostało zweryfikowane!'
    content = f'Dzień dobry, {user.first_name}!\nZ przyjemnością informujemy, że Twoje konto {user.username} w ' \
              f'serwisie Usamodzielnieni zostało pomyślnie zweryfikowane. Możesz teraz zalogować się i korzystać ' \
              f'ze wszystkich dostępnych funkcji:\n{login_url}\nŻyczymy miłego dnia,\nZespół Usamodzielnionych'
    send_email(email, subject, content)


def send_rejection_email(pk):
    user = Account.objects.get(id=pk)
    email = user.email
    contact_email = settings.CONTACT_EMAIL
    subject = f'Twoje konto w serwisie Usamodzielnieni zostało zdezaktywowane'
    content = f'Dzień dobry, {user.first_name}!\nZ przykrością informujemy, że Twoje konto {user.username} w ' \
              f'serwisie Usamodzielnieni nie spełnia wymogów naszego regulaminu. Jeżeli uważasz, że zaszła pomyłka, ' \
              f'prosimy o kontakt na adres {contact_email}\n' \
              f'Życzymy miłego dnia,\nZespół Usamodzielnionych'
    send_email(email, subject, content)


def send_account_data_change_email(pk, data):
    user = Account.objects.get(id=pk)
    email = user.email
    contact_email = settings.CONTACT_EMAIL
    subject = f'Dane Twojego konta w serwisie Usamodzielnieni zostały zmienione'
    content_data = ''
    for key in data:
        key_name = type(user)._meta.get_field(key).verbose_name
        key_value = data[key]
        content_data += f'{key_name}: {key_value}\n'
    content = f'Dzień dobry, {user.first_name}!\nInformujemy, że dane Twojego konta w serwisie Usamodzielnieni ' \
              f'zostały zmienione. Nowe dane:\n{content_data}Jeżeli uważasz, że zaszła pomyłka, prosimy o kontakt ' \
              f'na adres {contact_email}\nŻyczymy miłego dnia,\nZespół Usamodzielnionych'
    send_email(email, subject, content)
