from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='classificacoesetarias_index'),
    path('listar/', views.lista_classificacoesetarias, name='lista_classificacoesetarias'),
    path('adicionar/', views.adicionar_classificacaoetaria, name='adicionar_classificacaoetaria'),
]
