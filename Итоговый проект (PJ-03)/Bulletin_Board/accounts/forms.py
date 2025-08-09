from django import forms

class ConfirmCodeForm(forms.Form):
    email = forms.EmailField(label='Email')
    code = forms.CharField(max_length=6, label='Код подтверждения')