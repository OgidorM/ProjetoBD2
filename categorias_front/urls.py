from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='categorias_index'),
    path('listar/', views.lista_categorias, name='lista_categorias'),
    path('adicionar/', views.adicionar_categoria, name='adicionar_categoria'),
]
