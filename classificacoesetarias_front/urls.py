from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='classificacoesetarias_index'),
    path('listar/', views.lista_classificacoesetarias, name='lista_classificacoesetarias'),
    path('adicionar/', views.adicionar_classificacaoetaria, name='adicionar_classificacaoetaria'),
    path('editar/<int:classificacaoid>/', views.editar_classificacaoetaria, name='editar_classificacaoetaria'),
    path('remover/<int:classificacaoid>/', views.remover_classificacaoetaria, name='remover_classificacaoetaria'),
]
