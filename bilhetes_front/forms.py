from django import forms
from bd2ap1.models import Bilhetes

class BilheteForm(forms.ModelForm):
    class Meta:
        model = Bilhetes
        fields = ["sessaoid", "lugarid", "precobilhete", "emissao"]
        widgets = {
            "sessaoid": forms.Select(attrs={"class": "form-select"}),
            "lugarid": forms.Select(attrs={"class": "form-select"}),
            "precobilhete": forms.NumberInput(attrs={"class": "form-control", "type": "number", "min": "0", "step": "0.01"}),
            "emissao": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }
