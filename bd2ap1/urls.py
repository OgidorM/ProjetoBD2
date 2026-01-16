from django.contrib import admin
from django.urls import path, include
from . import views
from .views import home
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # ← raiz do site
    path('filmes/', include('filmes_front.urls')),
    path('salas/', include('salas_front.urls')),
    path('lugares/', include('lugares_front.urls')),
    path('bilhetes/', include('bilhetes_front.urls')),
    path('produtos/', include('produtos_front.urls')),
    path('vendas/', include('vendas_front.urls')),
    path('vendaslinhas/', include('vendaslinhas_front.urls')),
    path('avaliacoes/', include('avaliacoes_front.urls')),
    #path('cinemas/', include('cinemas_front.urls')),

    # API endpoints
    path('api/filmes/', views.filmes_api, name='filmes_api'),
]