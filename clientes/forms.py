from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nomecliente', 'emailcliente', 'telefonecliente', 'datanascimento',
            'moradacliente', 'codigopostalcliente', 'localidadecliente', 'nif'
        ]

