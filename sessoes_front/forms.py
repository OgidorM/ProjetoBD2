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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert datetime to time for display if instance exists
        if self.instance and self.instance.pk:
            if self.instance.inicio and hasattr(self.instance.inicio, 'time'):
                self.initial['inicio'] = self.instance.inicio.time()
            if self.instance.fim and hasattr(self.instance.fim, 'time'):
                self.initial['fim'] = self.instance.fim.time()
