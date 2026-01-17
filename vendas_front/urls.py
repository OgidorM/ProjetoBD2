from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='vendas_index'),
    path('listar/', views.lista_vendas, name='lista_vendas'),
    path('adicionar/', views.adicionar_venda, name='adicionar_venda'),
    path('editar/<int:vendaid>/', views.editar_venda, name='editar_venda'),
    path('remover/<int:vendaid>/', views.remover_venda, name='remover_venda'),
    path('relatorios/mv-vendas-diarias.csv', views.export_mv_vendas_diarias_csv, name='export_mv_vendas_diarias_csv'),
]