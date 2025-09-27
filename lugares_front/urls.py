from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='lugares_index'),
    path('listar/', views.lista_lugares, name='lista_lugares'),
    path('adicionar/', views.adicionar_lugar, name='adicionar_lugar'),
]
