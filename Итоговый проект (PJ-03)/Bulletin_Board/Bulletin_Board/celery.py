import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Bulletin_Board.settings')

app = Celery('Bulletin_Board')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()