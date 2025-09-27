from django.urls import path
from . import views

urlpatterns = [
    path("", views.lista_salas, name="salas_index"),
    path("listar/", views.lista_salas, name="lista_salas"),
    path("adicionar/", views.adicionar_sala, name="adicionar_sala"),
   # path("editar/<int:sala_id>", views.editar_sala, name="sala_editar"),
    #path("apagar/<int:sala_id>", views.apagar_sala, name="sala_apagar"),
]