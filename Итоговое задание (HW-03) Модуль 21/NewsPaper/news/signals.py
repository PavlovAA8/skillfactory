from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Post
from allauth.account.signals import user_signed_up
from django.core.mail import send_mail
from django.template.loader import render_to_string

@receiver(pre_save, sender=Post)
def limit_posts_per_day(sender, instance, **kwargs):
    if instance.pk is None:
        now = timezone.now()
        start_time = now - timezone.timedelta(days=1)
        post_count = Post.objects.filter(
            author=instance.author,
            data_time_created__gte=start_time
        ).count()
        if post_count >= 3:
            raise ValueError("Автор не может создавать более 3 постов в сутки.")


@receiver(user_signed_up)
def send_welcome_email(request, user, **kwargs):
    context = {
        'username': user.username,
    }
    html_content = render_to_string('hello_mail.html', context)

    send_mail(
        subject='Спасибо за регистрацию на нашем сайте!',
        message='Это текстовое сообщение для почтовых клиентов, которые не поддерживают HTML.',
        from_email='XXX@yandex.ru',     # <-------------------- Почта отправителя
        recipient_list=[user.email],
        fail_silently=False,
        html_message=html_content,
    )