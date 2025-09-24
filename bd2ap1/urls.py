from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
<<<<<<< Updated upstream
=======
    path('', include('filmes_front.urls')),  # conecta a app frontend
>>>>>>> Stashed changes
]
