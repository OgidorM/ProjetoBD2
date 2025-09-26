from django import forms
from bd2ap1.models import VendaLinhas

class VendaLinhaForm(forms.ModelForm):
    class Meta:
        model = VendaLinhas
        fields = ["vendaid", "produtoid", "quantidade", "total_linha", "precolinha"]
        widgets = {
            "vendaid": forms.Select(attrs={"class": "form-select"}),
            "produtoid": forms.Select(attrs={"class": "form-select"}),
            "quantidade": forms.NumberInput(attrs={"class": "form-control", "type": "number", "min": "1"}),
            "total_linha": forms.NumberInput(attrs={"class": "form-control", "type": "number", "min": "0", "step": "0.01"}),
            "precolinha": forms.NumberInput(attrs={"class": "form-control", "type": "number", "min": "0", "step": "0.01"}),
        }