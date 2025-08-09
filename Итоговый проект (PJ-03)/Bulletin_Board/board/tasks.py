from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import ScheduledMessage
from mail_data import mail

User = get_user_model()

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_scheduled_message(self, message_id):
    try:
        msg = ScheduledMessage.objects.get(pk=message_id)
        subject = msg.title
        message = msg.content
        from_email = mail
        recipient_list = list(User.objects.filter(is_active=True).values_list('email', flat=True))
        recipient_list = [email for email in recipient_list if email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    except Exception as exc:
        raise self.retry(exc=exc)