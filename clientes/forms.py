# /home/driblades/Documents/BD2/b2da1/clientes/forms.py
from django import forms
# CORREÇÃO: Importar da tabela legada
from bd2ap1.models import Clientes as Cliente 

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nomecliente', 'emailcliente', 'telefonecliente', 'datanascimento',
            'moradacliente', 'codigopostalcliente', 'localidadecliente', 'nif'
        ]
        widgets = {
            'nomecliente': forms.TextInput(attrs={'class': 'form-control'}),
            'emailcliente': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefonecliente': forms.TextInput(attrs={'class': 'form-control'}),
            'datanascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'moradacliente': forms.TextInput(attrs={'class': 'form-control'}),
            'codigopostalcliente': forms.TextInput(attrs={'class': 'form-control'}),
            'localidadecliente': forms.TextInput(attrs={'class': 'form-control'}),
            'nif': forms.TextInput(attrs={'class': 'form-control'}),
        }