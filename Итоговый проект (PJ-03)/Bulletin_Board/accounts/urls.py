from django.urls import path, include
from .views import CustomSignupView, ConfirmByCodeView, ResendCodeView
from allauth.account import urls as allauth_urls

urlpatterns = [
    path('signup/', CustomSignupView.as_view(), name='account_signup'),
    path('confirm-code/', ConfirmByCodeView.as_view(), name='confirm_code'),
    path('resend-code/', ResendCodeView.as_view(), name='resend_code'),
    path('', include(allauth_urls)),
]