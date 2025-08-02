from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter, OAuth2LoginView, OAuth2CallbackView
import requests

class YandexOAuth2Adapter(OAuth2Adapter):
    provider_id = 'yandex'
    access_token_url = 'https://oauth.yandex.ru/token'
    authorize_url = 'https://oauth.yandex.ru/authorize'
    profile_url = 'https://login.yandex.ru/info'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url, params={'format': 'json', 'oauth_token': token.token})
        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)

oauth2_login = OAuth2LoginView.adapter_view(YandexOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(YandexOAuth2Adapter)