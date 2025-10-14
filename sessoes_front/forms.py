from django import forms
from bd2ap1.models import Sessoes

class SessaoForm(forms.ModelForm):
    ESTADO_CHOICES = [
        ('Ativa', 'Ativa'),
        ('Concluída', 'Concluída'),
        ('Agendada', 'Agendada'),
        ('Cancelada', 'Cancelada'),
    ]

    estadosessao = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        label='Estado da Sessão',
        widget=forms.Select(attrs={'class': 'form-select', 'style': 'max-width: 250px; display: inline-block;'})
    )

    class Meta:
        model = Sessoes
        fields = '__all__'
        labels = {
            'filmeid': 'Filme',
            'salaid': 'Sala',
            'inicio': 'Hora de Início',
            'fim': 'Hora de Fim',
            'versao': 'Versão (ex: Legendado, Dublado)',
            'estadosessao': 'Estado da Sessão',
            'precosessao': 'Preço da Sessão',
        }
        widgets = {
            'inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'style': 'max-width: 180px; display: inline-block;', 'step': '300'}),
            'fim': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'style': 'max-width: 180px; display: inline-block;', 'step': '300'}),
        }
