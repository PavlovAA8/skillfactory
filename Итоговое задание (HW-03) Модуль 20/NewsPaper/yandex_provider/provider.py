from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from .views import YandexOAuth2Adapter

class YandexAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('default_email')

    def to_str(self):
        return self.account.extra_data.get('real_name', super().to_str())

class YandexProvider(OAuth2Provider):
    id = 'yandex'
    name = 'Yandex'
    package = 'yandex_provider'
    oauth2_adapter_class = YandexOAuth2Adapter  

    def extract_uid(self, data):
        return str(data.get('id')) 

    def extract_common_fields(self, data):
        return dict(
            email=data.get('default_email'),
            username=data.get('login'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
        )

provider_classes = [YandexProvider]