from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from .models import Subscriber, Post, Category
from celery import shared_task


@shared_task
def send_weekly_digest():
    print("Задача send_weekly_digest запущена")
    now = timezone.now()
    week_ago = now - timezone.timedelta(days=7)
    subscribers = Subscriber.objects.select_related('user', 'category').all()
    user_posts = {}

    for subscriber in subscribers:
        user = subscriber.user
        category = subscriber.category

        if user not in user_posts:
            user_posts[user] = {
                'username': user.username,
                'email': user.email,
                'posts': []
            }

        posts = Post.objects.filter(
            postcategory__category=category,
            data_time_created__gte=week_ago
        )

        for post in posts:
            user_posts[user]['posts'].append({
                'title': post.title,
                'url': reverse('posts_detail', args=[post.id]),
                'category': category.name
            })

    for user, data in user_posts.items():
        if data['posts']:
            context = {
                'username': data['username'],
                'post_links': data['posts'],
            }
            html_content = render_to_string('weekly_digest.html', context)

            send_mail(
                subject='Новые посты за неделю',
                message='Смотрите новые посты за неделю!',
                from_email= "XXX@yandex.ru",     # <-------------------- Почта отправителя
                recipient_list=[data['email']],
                fail_silently=False,
                html_message=html_content,
            )

@shared_task
def send_new_post_notification(post_id, category_id):
    post = Post.objects.get(id=post_id)
    category = Category.objects.get(id=category_id)
    subscribers = Subscriber.objects.filter(category=category)
    
    for subscriber in subscribers:
        context = {
            'category_name': category.name,
            'post_title': post.title,
            'post_text': post.text,
            'post_type': 'Новость' if post.post_type == 'NW' else 'Статья',
            'post_url': f'http://127.0.0.1:8000/news/{post.id}/',
        }
        html_content = render_to_string('mail.html', context)

        msg = EmailMultiAlternatives(
            subject=f'Новый пост в категории {category.name}',
            body=f'Проверьте новый пост: {post.title}\n\n{post.text}',
            from_email='XXX@yandex.ru',      # <-------------------- Почта отправителя
            to=[subscriber.user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()