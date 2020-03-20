from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from src.account.utils import send_mail_via_sendgrid
from sendgrid.helpers.mail import Mail, PlainTextContent


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    reset_token_message = f'The token to reset your password is {reset_password_token.key}'
    message = Mail(
        from_email='noreply@usamodzielnieni.pl',
        to_emails=reset_password_token.user.email,
        subject='Password reset',
        plain_text_content=PlainTextContent(reset_token_message))

    send_mail_via_sendgrid(message)
