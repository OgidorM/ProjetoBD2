from django import forms
from bd2ap1.models import Produtos

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produtos
        fields = ["nomeproduto", "precoproduto", "stock", "ativo"]
        widgets = {
            "nomeproduto": forms.TextInput(attrs={"class": "form-control"}),
            "precoproduto": forms.NumberInput(attrs={"class": "form-control", "type": "number", "min": "0", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "type": "number", "min": "0"}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }