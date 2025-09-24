from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('', include('filmes_front.urls')),  # conecta a app frontend

]