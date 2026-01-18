from django.contrib import admin
from .models import (
    Categorias, Cinemas, ClassificacoesEtarias, Filmes, Salas, 
    Sessoes, Lugares, LugaresSessao, Clientes, Funcionarios, 
    Produtos, Vendas, Bilhetes, VendaLinhas, Avaliacoes
)

@admin.register(Avaliacoes)
class AvaliacoesAdmin(admin.ModelAdmin):
    list_display = ('avaliacaoid', 'get_venda', 'avaliacaocinema', 'avaliacaofilme', 'avaliacaofuncionario', 'tituloavaliacao')
    list_filter = ('avaliacaocinema', 'avaliacaofilme', 'avaliacaofuncionario')
    search_fields = ('tituloavaliacao', 'comentario', 'venda__vendaid')

    def get_venda(self, obj):
        return f"Venda #{obj.venda.vendaid}"
    get_venda.short_description = 'Venda'

@admin.register(Cinemas)
class CinemasAdmin(admin.ModelAdmin):
    list_display = ('nomecinema', 'localidadecinema', 'ranking')
    list_editable = ('ranking',)
    search_fields = ('nomecinema', 'localidadecinema')

@admin.register(Filmes)
class FilmesAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'produtora', 'ranking')
    list_filter = ('categoriaid', 'classificacaoetaria')
    search_fields = ('titulo', 'produtora')

@admin.register(Vendas)
class VendasAdmin(admin.ModelAdmin):
    list_display = ('vendaid', 'clienteid', 'data', 'totalvenda', 'estadovenda')
    list_filter = ('estadovenda', 'data')
    search_fields = ('vendaid', 'clienteid__nomecliente')

# Register other models simply
admin.site.register(Categorias)
admin.site.register(ClassificacoesEtarias)
admin.site.register(Salas)
admin.site.register(Sessoes)
admin.site.register(Lugares)
admin.site.register(LugaresSessao)
admin.site.register(Clientes)
admin.site.register(Funcionarios)
admin.site.register(Produtos)
admin.site.register(Bilhetes)
admin.site.register(VendaLinhas)