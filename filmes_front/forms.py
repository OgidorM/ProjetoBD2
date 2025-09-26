from django import forms
from bd2ap1.models import Filmes

class FilmeForm(forms.ModelForm):
    class Meta:
        model = Filmes
        fields = [
            "titulo",
            "categoriaid",
            "cinemaid",
            "datalancamento",
            "duracao",
            "produtora",
            "fimexebicao",
            "idioma",
            "sinopse",
            "classificacaoetaria",
        ]
        widgets = {
            "datalancamento": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "fimexebicao": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "sinopse": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "duracao": forms.NumberInput(attrs={"type": "number", "class": "form-control"}),
            "produtora": forms.TextInput(attrs={"class": "form-control"}),
            "idioma": forms.TextInput(attrs={"class": "form-control"}),
            "classificacaoetaria": forms.Select(attrs={"class": "form-select"}),
            "categoriaid": forms.Select(attrs={"class": "form-select"}),
            "cinemaid": forms.Select(attrs={"class": "form-select"}),
        }
