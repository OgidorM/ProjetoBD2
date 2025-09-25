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
        fields = ["cinemaid", "nomesala", "capacidade", "tiposala"]
        widgets = {
            "cinemaid": forms.Select(attrs={'class': 'form-select'}),
            "nomesala": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Sala'}),
            "capacidade": forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            "tiposala": forms.Select(choices=TIPO, attrs={'class': 'form-select'}),
        }