from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from news.models import Author

User = get_user_model()

@receiver(post_save, sender=User)
def add_to_common_group(sender, instance, created, **kwargs):
    if created:
        common_group, _ = Group.objects.get_or_create(name='common')
        instance.groups.add(common_group)

@receiver(m2m_changed, sender=User.groups.through)
def sync_author_with_group(sender, instance, **kwargs):
    authors_group, _ = Group.objects.get_or_create(name='authors')

    if authors_group in instance.groups.all():
        Author.objects.get_or_create(user=instance)
    else:
        Author.objects.filter(user=instance).delete()