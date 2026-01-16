from django.contrib import admin
from django.urls import path, include
from bd2ap1.views import home, SignUpView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    # MVC-style controllers
    path('cinemas/', include('cinemas.urls')),
    path('clientes/', include('clientes.urls')),
    path('funcionarios/', include('funcionarios.urls')),
    # Legacy/front apps
    path('filmes/', include('filmes_front.urls')),
    path('salas/', include('salas_front.urls')),
    path('lugares/', include('lugares_front.urls')),
    path('bilhetes/', include('bilhetes_front.urls')),
    path('produtos/', include('produtos_front.urls')),
    path('vendas/', include('vendas_front.urls')),
    path('vendaslinhas/', include('vendaslinhas_front.urls')),
    path('avaliacoes/', include('avaliacoes_front.urls')),
    path('sessoes/', include('sessoes_front.urls')),
    path('categorias/', include('categorias_front.urls')),
    path('classificacoesetarias/', include('classificacoesetarias_front.urls')),

    path('accounts/', include('django.contrib.auth.urls')),

    path('accounts/signup/', SignUpView.as_view(), name='signup'),
]
