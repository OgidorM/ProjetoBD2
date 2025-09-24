from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('filmes/', views.lista_filmes, name='lista_filmes'),
    path('adicionar/', views.adicionar_filme, name='adicionar_filme'),  # remove por enquanto
]
