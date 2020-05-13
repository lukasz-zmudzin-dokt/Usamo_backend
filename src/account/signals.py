from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created

from django.conf import settings
from .utils import send_mail_via_sendgrid
from sendgrid.helpers.mail import Mail, PlainTextContent
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    reset_token_message = f'The token to reset your password is {reset_password_token.key}'
    message = Mail(
        from_email='noreply@usamodzielnieni.pl',
        to_emails=reset_password_token.user.email,
        subject='Password reset',
        plain_text_content=PlainTextContent(reset_token_message))

    send_mail_via_sendgrid(message)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def commit_date_joined(sender, instance, created, **kwargs):
    if created:
        instance.date_joined = timezone.now()


def commit_last_login(sender, user, request, **kwargs):
    user.last_login = timezone.now()


user_logged_in.connect(commit_last_login)
