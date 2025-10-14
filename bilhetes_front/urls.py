from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='bilhetes_index'),
    path('listar/', views.lista_bilhetes, name='lista_bilhetes'),
    path('adicionar/', views.adicionar_bilhete, name='adicionar_bilhete'),
    path('editar/<int:bilheteid>/', views.editar_bilhete, name='editar_bilhete'),
    path('remover/<int:bilheteid>/', views.remover_bilhete, name='remover_bilhete'),
]
