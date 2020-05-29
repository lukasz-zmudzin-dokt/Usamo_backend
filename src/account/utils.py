import uuid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings


def send_mail_via_sendgrid(message: Mail):
    try:
        api_key = settings.SENDGRID_API_KEY
        sg = SendGridAPIClient(api_key)
        message.template_id = settings.SENDGRID_TEMPLATE_ID
        sg.send(message)
    except Exception as e:
        print(e)


def __create_file_path(folder, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(f'account/{folder}', filename)


def create_profile_picture_file_path(instance, filename):
    return __create_file_path('profile_pics', filename)
