from django import forms
from django.contrib.auth.models import User
from .models import Funcionario


class FuncionarioForm(forms.ModelForm):
    # Credenciais (somente para criação)
    username = forms.CharField(
        max_length=150,
        required=False,
        help_text='Username do login (obrigatório ao criar).',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Password inicial (obrigatória ao criar).'
    )

    class Meta:
        model = Funcionario
        fields = [
            'cinemaid', 'nomefuncionario', 'emailfuncionario', 'telefonefuncionario',
            'cargo', 'admissao', 'salario', 'ranking'
        ]
        widgets = {
            'cinemaid': forms.Select(attrs={'class': 'form-select'}),
            'nomefuncionario': forms.TextInput(attrs={'class': 'form-control'}),
            'emailfuncionario': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefonefuncionario': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'admissao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'ranking': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '5'}),
        }

    def clean_ranking(self):
        value = self.cleaned_data.get('ranking')
        if value is None:
            return value
        if value < 0 or value > 5:
            raise forms.ValidationError('Ranking must be between 0 and 5.')
        return value

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este username já existe.')
        return username
