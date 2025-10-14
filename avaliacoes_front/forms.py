from django import forms
from bd2ap1.models import Avaliacoes

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacoes
        fields = ["venda", "tituloavaliacao", "avaliacaocinema", "avaliacaofilme", "avaliacaofuncionario", "comentario"]
        widgets = {
            "venda": forms.Select(attrs={"class": "form-select"}),
            "tituloavaliacao": forms.TextInput(attrs={"class": "form-control"}),
            "avaliacaocinema": forms.NumberInput(attrs={"class": "form-control", "type": "number", "min": "1", "max": "5"}),
            "avaliacaofilme": forms.NumberInput(attrs={"class": "form-control", "type": "number", "min": "1", "max": "5"}),
            "avaliacaofuncionario": forms.NumberInput(attrs={"class": "form-control", "type": "number", "min": "1", "max": "5"}),
            "comentario": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }