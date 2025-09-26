from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='produtos_index'),
    path('listar/', views.lista_produtos, name='lista_produtos'),
    path('adicionar/', views.adicionar_produto, name='adicionar_produto'),
]