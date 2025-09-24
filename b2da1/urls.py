from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('filmes_front.urls')),
    path('', include('bd2ap1.urls')),
]
