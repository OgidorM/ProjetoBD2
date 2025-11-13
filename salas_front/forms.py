from django import forms
from bd2ap1.models import Salas

TIPO = [
    ("Standard", "Standard"),
    ("VIP", "VIP"),
    ("IMAX", "IMAX"),
]

class SalaForm(forms.ModelForm):
    class Meta:
        model = Salas
        fields = ["cinemaid", "nomesala", "capacidade", "filas", "colunas", "tiposala"]
        widgets = {
            "cinemaid": forms.Select(attrs={'class': 'form-select'}),
            "nomesala": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Sala'}),
            "capacidade": forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            "filas": forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            "colunas": forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            "tiposala": forms.Select(choices=TIPO, attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        capacidade = cleaned_data.get('capacidade')
        filas = cleaned_data.get('filas')
        colunas = cleaned_data.get('colunas')

        if filas and colunas and capacidade:
            if filas * colunas > capacidade:
                raise forms.ValidationError(
                    f"O número de assentos (filas x colunas = {filas * colunas}) "
                    f"não pode ser maior que a capacidade da sala ({capacidade})."
                )
        return cleaned_data