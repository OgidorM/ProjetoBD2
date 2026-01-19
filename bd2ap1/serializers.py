from rest_framework import serializers
from .models import Filmes, Categorias, ClassificacoesEtarias, Cinemas, Sessoes, Salas, Lugares, LugaresSessao, Produtos

class ProdutosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produtos
        fields = ['produtoid', 'nomeproduto', 'precoproduto', 'stock', 'ativo']

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
        fields = [
            'cinemaid', 'nomecinema', 'emailcinema', 'telefonecinema', 
            'moradacinema', 'codigopostalcinema', 'localidadecinema', 'ranking'
        ]


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
            'cartaz_url',
            'ranking',
            'categoria',
            'classificacao',
            'cinema'
        ]

class SalasSerializer(serializers.ModelSerializer):
    cinema = CinemasSerializer(source='cinemaid', read_only=True)
    class Meta:
        model = Salas
        fields = ['salaid', 'nomesala', 'tiposala', 'cinema']

class SessoesSerializer(serializers.ModelSerializer):
    sala = SalasSerializer(source='salaid', read_only=True)
    
    class Meta:
        model = Sessoes
        fields = ['sessaoid', 'sala', 'filmeid', 'inicio', 'fim', 'versao', 'precosessao']

class SessaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sessoes
        fields = ['sessaoid', 'salaid', 'filmeid', 'inicio', 'fim', 'versao', 'estadosessao', 'precosessao']

class LugaresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lugares
        fields = ['lugarid', 'fila', 'numero', 'tipolugar']

class LugaresSessaoSerializer(serializers.ModelSerializer):
    lugar = LugaresSerializer(source='lugarid', read_only=True)
    
    class Meta:
        model = LugaresSessao
        fields = ['lugarsessaoid', 'lugar', 'estado']

