from django import forms
from bd2ap1.models import Lugares, Salas

TIPO = [
    ("Standard", "Standard"),
    ("VIP", "VIP"),
    ("Acessivel", "Acessível"),
]
ESTADO = [
    ("Disponivel", "Disponível"),
    ("Indisponivel", "Indisponível"),
]

class LugarForm(forms.ModelForm):
    class Meta:
        model = Lugares
        fields = ["salaid", "fila", "numero", "tipolugar", "estadolugar"]
        widgets = {
            "salaid": forms.Select(attrs={"class": "form-select"}),
            "fila": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: A"}),
            "numero": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "tipolugar": forms.Select(choices=TIPO, attrs={"class": "form-select"}),
            "estadolugar": forms.Select(choices=ESTADO, attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['salaid'].queryset = Salas.objects.all()
