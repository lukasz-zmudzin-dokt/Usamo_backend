import os
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
