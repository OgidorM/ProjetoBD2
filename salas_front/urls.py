from django.urls import path
from . import views

urlpatterns = [
    path("", views.lista_salas, name="salas_index"),
    path("listar/", views.lista_salas, name="lista_salas"),
    path("adicionar/", views.adicionar_sala, name="adicionar_sala"),
    path("editar/<int:salaid>", views.editar_sala, name="editar_sala"),
    path("apagar/<int:salaid>", views.remover_sala, name="apagar_sala"),
]