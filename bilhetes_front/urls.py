from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='bilhetes_index'),
    path('listar/', views.lista_bilhetes, name='lista_bilhetes'),
    path('adicionar/', views.adicionar_bilhete, name='adicionar_bilhete'),
]
