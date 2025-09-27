from django import forms
from .models import Cinema


class CinemaForm(forms.ModelForm):
    class Meta:
        model = Cinema
        # Explicitly list editable fields (exclude ID & computed fields)
        fields = [
            'nomecinema', 'emailcinema', 'telefonecinema', 'moradacinema',
            'codigopostalcinema', 'localidadecinema', 'ranking'
        ]

    def clean_ranking(self):
        value = self.cleaned_data.get('ranking')
        if value is None:
            return value
        if value < 0 or value > 5:
            raise forms.ValidationError('Ranking must be between 0 and 5.')
        return value

