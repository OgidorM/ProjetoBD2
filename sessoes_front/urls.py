from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='sessoes_index'),
    path('listar/', views.lista_sessoes, name='lista_sessoes'),
    path('adicionar/', views.adicionar_sessao, name='adicionar_sessao'),
]
