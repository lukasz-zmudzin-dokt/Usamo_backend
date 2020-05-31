from apscheduler.schedulers.background import BackgroundScheduler
from notifications.signals import notify
from python_http_client import ForbiddenError
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.utils import timezone
from account.models import Account
from django.conf import settings
from sendgrid.helpers.mail import Mail
from account.utils import send_mail_via_sendgrid
from account.account_type import AccountType
from job.models import JobOffer
from django_apscheduler.models import DjangoJob

# DjangoJob.objects.filter(next_run_time__lt=timezone.now()).delete()

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


def send_email(email, subject, name, part1=None, part2=None, part3=None):
    message = Mail(
        from_email='no-reply@usamodzielnieni.pl',
        to_emails=email
    )
    message.dynamic_template_data = {
        'subject': subject,
        'name': name,
        'part1': part1,
        'part2': part2,
        'part3': part3
    }
    
    send_mail_via_sendgrid(message)


def send_notification_email(pk):
    user = Account.objects.get(id=pk)
    email = user.email
    login_url = settings.FRONT_URL + 'login'
    notifications = user.notifications.filter(unread=True)

    if notifications.count() > 0:
        subject = 'Usamodzielnieni: nowe powiadomienia'
        part1 = f'Masz {notifications.count()} nieodczytane powiadomienia.'
        part2 = 'Aby je wyświetlić, zaloguj się, korzystając z poniższego linka:'
        part3 = login_url
        send_email(email, subject, user.first_name, part1=part1, part2=part2, part3=part3)
   


def send_verification_email(pk):
    user = Account.objects.get(id=pk)
    email = user.email
    login_url = settings.FRONT_URL + 'login'
    subject = f'Usamodzielnieni: twoje konto zostało zweryfikowane'
    part1 =   f'Z przyjemnością informujemy, że Twoje konto {user.username} w ' \
              f'serwisie Usamodzielnieni zostało pomyślnie zweryfikowane. Możesz teraz zalogować się i korzystać ' \
              f'ze wszystkich dostępnych funkcji:'
    part2 = login_url
    send_email(email, subject, user.first_name, part1=part1, part2=part2)


def send_rejection_email(pk):
    user = Account.objects.get(id=pk)
    email = user.email
    contact_email = settings.CONTACT_EMAIL
    subject = f'Usamodzielnieni: twoje konto zostało zdezaktywowane'
    part1 =   f'Z przykrością informujemy, że Twoje konto {user.username} w ' \
              f'serwisie Usamodzielnieni nie spełnia wymogów naszego regulaminu.' 
    part2 =   f'Jeżeli uważasz, że zaszła pomyłka, prosimy o kontakt na adres {contact_email}' 
             
    send_email(email, subject, user.first_name, part1=part1, part2=part2)


def send_account_data_change_email(pk, data):
    user = Account.objects.get(id=pk)
    email = user.email
    contact_email = settings.CONTACT_EMAIL
    subject = f'Usamodzielnieni: dane konta zostały zmienione'
    
    part1 =   'Informujemy, że dane Twojego konta w serwisie Usamodzielnieni zostały zmienione przez pracownika fundacji.' 
    part2 = None
    if 'username' and 'password' in data:
        part1 += ' Oto nowe dane do logowania:'
        part2 = f"Login: {data['username']}, hasło: {data['password']}"   
    part3 =   f'Jeżeli uważasz, że zaszła pomyłka, prosimy o kontakt ' \
              f'na adres {contact_email}'

    send_email(email, subject, user.first_name, part1=part1, part2=part2, part3=part3)
