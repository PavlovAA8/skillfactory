from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import FormView, View
from allauth.account.models import EmailConfirmation, EmailAddress, EmailConfirmation
from .forms import ConfirmCodeForm
from allauth.account.views import SignupView as AllauthSignupView
from django.views import View
from django.template.loader import render_to_string
from django.core.mail import send_mail
import secrets
from django.conf import settings


CODE_EXPIRE_MINUTES = 60 

class ConfirmByCodeView(FormView):
    template_name = 'confirm_code.html'
    form_class = ConfirmCodeForm
    success_url = reverse_lazy('account_login')  # куда редиректить после подтверждения

    def get_initial(self):
        initial = super().get_initial()
        email = self.request.GET.get('email')
        if email:
            initial['email'] = email
        return initial

    def form_valid(self, form):
        email = form.cleaned_data['email'].strip().lower()
        code = form.cleaned_data['code'].strip()

        # Ищем confirmation по ключу и email
        confirmation = (EmailConfirmation.objects
                        .filter(key=code, email_address__email__iexact=email)
                        .select_related('email_address__user')
                        .order_by('-sent')
                        .first())

        if not confirmation:
            form.add_error('code', 'Неверный код или email.')
            return self.form_invalid(form)

        # Проверяем срок годности
        sent = confirmation.sent
        if sent and timezone.now() - sent > timedelta(minutes=CODE_EXPIRE_MINUTES):
            form.add_error('code', 'Срок действия кода истёк. Запросите новый код.')
            return self.form_invalid(form)

        try:
            # подтверждаем email
            confirmation.confirm(self.request)
        except Exception as e:
            form.add_error(None, 'Ошибка при подтверждении: %s' % e)
            return self.form_invalid(form)

        # активируем пользователя и логиним
        user = confirmation.email_address.user
        if not user.is_active:
            user.is_active = True
            user.save()

        # логиним
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')

        messages.success(self.request, 'Email подтверждён и вы вошли в систему.')
        return super().form_valid(form)


class ResendCodeView(View):
    def post(self, request, *args, **kwargs):
        email = (request.POST.get('email') or '').strip().lower()
        if not email:
            messages.error(request, 'Email не указан.')
            return redirect(reverse('confirm_code'))

        try:
            email_address = EmailAddress.objects.get(email__iexact=email)
        except EmailAddress.DoesNotExist:
            messages.error(request, 'Email не найден.')
            return redirect(reverse('confirm_code'))

        # Удаляем старые подтверждения и создаём новый
        EmailConfirmation.objects.filter(email_address=email_address).delete()
        confirmation = EmailConfirmation.create(email_address)

        # Генерируем 6-значный код и сохраняем
        code = f"{secrets.randbelow(1_000_000):06d}"
        confirmation.key = code
        confirmation.sent = timezone.now()
        confirmation.save()

        # Отправляем письмо с кодом
        ctx = {'code': code, 'email': email}
        subject = 'Новый код подтверждения'
        message = render_to_string('account/email/code_confirmation.txt', ctx)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

        messages.success(request, 'Новый код отправлен на почту.')

        # Перенаправляем обратно на страницу ввода кода с email в GET
        return redirect(f"{reverse('confirm_code')}?email={email}")
    

class CustomSignupView(AllauthSignupView):
    def form_valid(self, form):
        # выполнит стандартное создание аккаунта (и отправку подтверждений)
        response = super().form_valid(form)

        # берём email из формы
        email = form.cleaned_data.get('email')

        # Перенаправляем на страницу ввода кода, передавая email в GET
        return redirect(f"{reverse_lazy('confirm_code')}?email={email}")