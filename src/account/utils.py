import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_mail_via_sendgrid(message: Mail):
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        raise e
