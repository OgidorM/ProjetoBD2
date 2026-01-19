from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='filmes_index'),
    path('listar/', views.lista_filmes, name='lista_filmes'),
    path('adicionar/', views.adicionar_filme, name='adicionar_filme'),
    path('importar-sinopses/', views.importar_sinopses, name='importar_sinopses'),
    path('detalhe/<int:filme_id>/', views.filme_detalhe_api, name='filme_detalhe_api'),
]
