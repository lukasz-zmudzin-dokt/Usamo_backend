import os
import uuid

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_mail_via_sendgrid(message: Mail):
    try:
        api_key = os.environ.get('SENDGRID_API_KEY')
        if api_key is None or not api_key:
            raise EnvironmentError('The api key has not been provided')

        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        raise e


def __create_file_path(folder, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(f'account/{folder}', filename)


def create_profile_picture_file_path(instance, filename):
    return __create_file_path('profile_pics', filename)
