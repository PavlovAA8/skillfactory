from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Comment
from mail_data import mail

@receiver(post_save, sender=Comment)
def send_comment_notification(sender, instance, created, **kwargs):
    if created:
        announcement = instance.announcement
        if instance.user != announcement.author:
            subject = f'Новый комментарий к объявлению "{announcement.title}"'
            message = f'Пользователь {instance.user.username} оставил новый комментарий к вашему объявлению.\n\n' \
                    f'Текст комментария: {instance.content}\n\n' \
                    f'Ссылка на объявление: http://127.0.0.1:8000/announcements/{announcement.id}/'
            recipient_list = [announcement.author.email]

            send_mail(subject, message, mail, recipient_list)


@receiver(post_save, sender=Comment)
def send_comment_accepted_email(sender, instance, created, **kwargs): 
    if not created :
        old_accepted = Comment.objects.get(pk=instance.pk).accepted
        if old_accepted is True:
            subject = f"Ваш комментарий к объявлению '{instance.announcement.title}' был принят."
            message = f"Здравствуйте, {instance.user.username}!\n\nВаш комментарий '{instance.content}' к объявлению '{instance.announcement.title}' был принят.\n\n" \
                        f'Ссылка на объявление: http://127.0.0.1:8000/announcements/{instance.announcement.id}/'
            
            recipient_list = [instance.user.email]

            send_mail(subject, message, mail, recipient_list)
