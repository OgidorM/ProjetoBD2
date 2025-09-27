from django import forms
from bd2ap1.models import Categorias

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categorias
        fields = '__all__'
        labels = {
            'nomecategoria': 'Nome da Categoria',
        }
