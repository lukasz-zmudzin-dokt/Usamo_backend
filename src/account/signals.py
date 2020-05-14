from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from .utils import send_mail_via_sendgrid
from sendgrid.helpers.mail import Mail, PlainTextContent
from usamo.settings.settings import PASS_RESET_URL


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    reset_url = PASS_RESET_URL + reset_password_token.key
    reset_token_message = f'Aby zresetować hasło, kliknij w poniższy link i postępuj zgodnie ze wskazówkami:\n{reset_url}\n\n' + \
    'Jeśli nie prosiłeś o zmianę hasła, zignoruj ten link i skontaktuj się z pomocą techniczną.'
    message = Mail(
        from_email='noreply@usamodzielnieni.pl',
        to_emails=reset_password_token.user.email,
        subject='Resetowanie hasła',
        plain_text_content=PlainTextContent(reset_token_message))

    send_mail_via_sendgrid(message)
