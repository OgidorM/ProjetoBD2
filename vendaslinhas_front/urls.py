from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='vendaslinhas_index'),
    path('listar/', views.lista_vendaslinhas, name='lista_vendaslinhas'),
    path('adicionar/', views.adicionar_vendalinha, name='adicionar_vendalinha'),
]