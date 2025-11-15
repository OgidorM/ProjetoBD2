from django import forms
from bd2ap1.models import Bilhetes, LugaresSessao

class BilheteForm(forms.ModelForm):
    class Meta:
        model = Bilhetes
        fields = ["lugarid", "precobilhete", "emissao"]
        widgets = {
            "sessao": forms.Select(attrs={
                "class": "form-select"
            }),
            "lugarid": forms.Select(attrs={
                "class": "form-select"
            }),
            "precobilhete": forms.NumberInput(attrs={
                "class": "form-control", 
                "type": "number", 
                "min": "0", 
                "step": "0.01"
            }),
            "emissao": forms.DateInput(attrs={
                "class": "form-control", 
                "type": "date"
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lugarid'].queryset = LugaresSessao.objects.filter(estado='Disponível')
