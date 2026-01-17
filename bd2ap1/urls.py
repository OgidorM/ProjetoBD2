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
    path('api/filmes/<int:filmeid>/sessoes/', views.sessoes_por_filme_api, name='sessoes_por_filme_api'),
    path('api/sessoes/<int:sessaoid>/lugares/', views.lugares_sessao_api, name='lugares_sessao_api'),
    path('api/vendas/criar/', views.criar_venda_api, name='criar_venda_api'),
    path('api/vendas/minhas/', views.minhas_vendas_api, name='minhas_vendas_api'),
    path('api/sessoes/criar/', views.criar_sessao_api, name='criar_sessao_api'),
    path('api/salas/', views.salas_api, name='salas_api'),
    path('api/login/', views.login_api, name='login_api'),
    path('api/signup/', views.signup_api, name='signup_api'),
]