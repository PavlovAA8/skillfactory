from django.apps import AppConfig

class YandexProviderConfig(AppConfig):
    name = 'yandex_provider'

    def ready(self):
        from allauth.socialaccount import providers
        from .provider import YandexProvider
        providers.registry.register(YandexProvider)