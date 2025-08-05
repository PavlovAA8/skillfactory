from .celery import app as celery_app

default_app_config = 'yandex_provider.apps.YandexProviderConfig'
__all__ = ('celery_app',)
