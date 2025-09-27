from django import forms
from .models import Funcionario


class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = [
            'cinemaid', 'nomefuncionario', 'emailfuncionario', 'telefonefuncionario',
            'cargo', 'admissao', 'salario', 'ranking'
        ]

    def clean_ranking(self):
        value = self.cleaned_data.get('ranking')
        if value is None:
            return value
        if value < 0 or value > 5:
            raise forms.ValidationError('Ranking must be between 0 and 5.')
        return value

