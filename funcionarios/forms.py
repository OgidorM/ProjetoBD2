from django import forms
from .models import Funcionario


class FuncionarioForm(forms.ModelForm):
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
