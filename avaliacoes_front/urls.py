from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='avaliacoes_index'),
    path('listar/', views.lista_avaliacoes, name='lista_avaliacoes'),
    path('adicionar/', views.adicionar_avaliacao, name='adicionar_avaliacao'),
]