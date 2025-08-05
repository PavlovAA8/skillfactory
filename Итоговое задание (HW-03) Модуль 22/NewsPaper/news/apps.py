from django.apps import AppConfig

class NewsConfig(AppConfig):
    name = 'news'

    def ready(self):
        import news.signals
        from . import scheduler
        scheduler.start()