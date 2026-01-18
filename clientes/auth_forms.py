from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class ClienteSignupForm(forms.Form):
    """Form HTML simples para signup de cliente (username + email + password)."""

    username = forms.CharField(max_length=150, label='Username')
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirmar Password')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este username já existe.')
        return username

    def clean_password1(self):
        pw = self.cleaned_data['password1']
        validate_password(pw)
        return pw

    def clean(self):
        cleaned = super().clean()
        pw1 = cleaned.get('password1')
        pw2 = cleaned.get('password2')
        if pw1 and pw2 and pw1 != pw2:
            self.add_error('password2', 'As passwords não coincidem.')
        return cleaned

