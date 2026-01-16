from rest_framework import serializers
from .models import Filmes, Categorias, ClassificacoesEtarias, Cinemas


class CategoriasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorias
        fields = ['categoriaid', 'nomecategoria']


class ClassificacoesEtariasSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassificacoesEtarias
        fields = ['classificacaoid', 'nomeclassificacao']


class CinemasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinemas
        fields = ['cinemaid', 'nomecinema', 'localidadecinema']


class FilmesSerializer(serializers.ModelSerializer):
    categoria = CategoriasSerializer(source='categoriaid', read_only=True)
    classificacao = ClassificacoesEtariasSerializer(source='classificacaoetaria', read_only=True)
    cinema = CinemasSerializer(source='cinemaid', read_only=True)

    class Meta:
        model = Filmes
        fields = [
            'filmeid',
            'titulo',
            'datalancamento',
            'duracao',
            'produtora',
            'idioma',
            'sinopse',
            'ranking',
            'categoria',
            'classificacao',
            'cinema'
        ]

