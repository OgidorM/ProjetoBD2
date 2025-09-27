from django import forms
from bd2ap1.models import ClassificacoesEtarias

class ClassificacaoEtariaForm(forms.ModelForm):
    class Meta:
        model = ClassificacoesEtarias
        fields = '__all__'
        labels = {
            'nomeclassificacao': 'Nome da Classificação Etária',
        }
