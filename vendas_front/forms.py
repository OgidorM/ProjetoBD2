from django import forms
from bd2ap1.models import Vendas

class VendaForm(forms.ModelForm):
    class Meta:
        model = Vendas
        fields = ["clienteid", "funcionarioid", "data", "estadovenda", "totalvenda"]
        widgets = {
            "clienteid": forms.Select(attrs={"class": "form-select"}),
            "funcionarioid": forms.Select(attrs={"class": "form-select"}),
            "data": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "estadovenda": forms.TextInput(attrs={"class": "form-control"}),
            "totalvenda": forms.NumberInput(attrs={"class": "form-control", "type": "number", "min": "0", "step": "0.01"}),
        }