import secrets
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.mail import send_mail
from allauth.account.signals import user_signed_up
from allauth.account.models import EmailConfirmation, EmailAddress
from django.conf import settings

CODE_LEN = 6

def _gen_code():
    return f"{secrets.randbelow(10**CODE_LEN):0{CODE_LEN}d}"

@receiver(user_signed_up)
def send_confirmation_code_after_signup(request, user, **kwargs):
    email = (user.email or '').lower()
    if not email:
        return

    #Получаем или создаём EmailAddress
    email_address, created = EmailAddress.objects.get_or_create(
        user=user,
        email=email,
        defaults={'verified': False, 'primary': True}
    )

    #Удаляем старые подтверждения для этого email_address
    EmailConfirmation.objects.filter(email_address=email_address).delete()

    #Создаём новый EmailConfirmation (allauth helper)
    confirmation = EmailConfirmation.create(email_address)

    #Заменяем key на числовой код и сохраняем
    code = _gen_code()
    confirmation.key = code
    confirmation.sent = timezone.now()
    confirmation.save()

    #Подготавливаем и отправляем письмо
    ctx = {
        'code': code,
        'email': email,
        'site_name': getattr(settings, 'SITE_NAME', ''),
    }

    subject = 'Код подтверждения регистрации'
    message = render_to_string('account/email/code_confirmation.txt', ctx)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])