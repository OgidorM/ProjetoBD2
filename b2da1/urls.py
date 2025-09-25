from django.contrib import admin
from django.urls import path, include
from bd2ap1.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    
    path('filmes/', include('filmes_front.urls')),
    path('salas/', include('salas_front.urls')),
    path('lugares/', include('lugares_front.urls')),
    path('bilhetes/', include('bilhetes_front.urls')),
]
