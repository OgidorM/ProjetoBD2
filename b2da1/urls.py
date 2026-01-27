from django.contrib import admin
from django.urls import path, include
from bd2ap1.views import home, SignUpView
from bd2ap1 import views as api_views

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
    # API endpoints
    path('api/whoami/', api_views.whoami_api, name='whoami_api'),
    path('api/cinemas/', api_views.cinemas_api, name='cinemas_api'),
    path('api/filmes/', api_views.filmes_api, name='filmes_api'),
    path('api/produtos/', api_views.produtos_api, name='produtos_api'),
    path('api/produtos/comprar/', api_views.comprar_produtos_api, name='comprar_produtos_api'),
    path('api/filmes/<int:filmeid>/sessoes/', api_views.sessoes_por_filme_api, name='sessoes_por_filme_api'),
    path('api/sessoes/<int:sessaoid>/lugares/', api_views.lugares_sessao_api, name='lugares_sessao_api'),
    path('api/vendas/criar/', api_views.criar_venda_api, name='criar_venda_api'),
    path('api/vendas/minhas/', api_views.minhas_vendas_api, name='minhas_vendas_api'),
    path('api/vendas/<int:vendaid>/digital/', api_views.fatura_digital_api, name='fatura_digital_api'),
    path('api/admin/vendas/exportar/', api_views.exportar_faturas_dia_api, name='exportar_faturas_dia_api'),
    path('api/avaliacoes/criar/', api_views.criar_avaliacao_api, name='criar_avaliacao_api'),
    path('api/sessoes/', api_views.lista_sessoes_api, name='lista_sessoes_api'),
    path('api/sessoes/<int:sessaoid>/deletar/', api_views.deletar_sessao_api, name='deletar_sessao_api'),
    path('api/sessoes/<int:sessaoid>/atualizar/', api_views.atualizar_sessao_api, name='atualizar_sessao_api'),
    path('api/sessoes/<int:sessaoid>/bilhetes/', api_views.bilhetes_sessao_api, name='bilhetes_sessao_api'),
    path('api/bilhetes/<int:bilheteid>/digital/', api_views.bilhete_digital_api, name='bilhete_digital_api'),
    path('api/bilhetes/<int:bilheteid>/cancelar/', api_views.cancelar_bilhete_api, name='cancelar_bilhete_api'),
    path('api/sessoes/criar/', api_views.criar_sessao_api, name='criar_sessao_api'),
    path('api/salas/', api_views.salas_api, name='salas_api'),
    path('api/login/', api_views.login_api, name='login_api'),
    path('api/logout/', api_views.logout_api, name='logout_api'),
    path('api/signup/', api_views.signup_api, name='signup_api'),
    path('api/produtos/', api_views.produtos_api, name='produtos_api'),
    path('api/produtos/comprar/', api_views.comprar_produtos_api, name='comprar_produtos_api'),
    path('api/user/update/', api_views.update_profile_api, name='update_profile_api'),
    path('api/admin/avaliacoes/', api_views.admin_avaliacoes_api, name='admin_avaliacoes_api'),
    path('api/admin/vendas/', api_views.admin_vendas_api, name='admin_vendas_api'),
    path('api/admin/vendas/exportar/', api_views.exportar_faturas_dia_api, name='exportar_faturas_dia_api'),
    path('api/admin/funcionarios/', api_views.admin_funcionarios_api, name='admin_funcionarios_api'),
    path('api/admin/funcionarios/<int:pk>/', api_views.admin_funcionario_detail_api,
         name='admin_funcionario_detail_api'),
    path('api/admin/clientes/', api_views.admin_clientes_api, name='admin_clientes_api'),
    path('api/admin/clientes/<int:pk>/', api_views.admin_cliente_detail_api, name='admin_cliente_detail_api'),
    path('api/admin/produtos/criar/', api_views.admin_create_produto_api, name='admin_create_produto_api'),
    path('api/admin/produtos/<int:pk>/', api_views.admin_produto_detail_api, name='admin_produto_detail_api'),
    path('api/admin/cinemas/criar/', api_views.admin_create_cinema_api, name='admin_create_cinema_api'),
    path('api/admin/cinemas/<int:cinema_id>/salas/criar/', api_views.admin_create_room_api, name='admin_create_room_api'),
    path('api/admin/filmes/criar/', api_views.admin_create_movie_api, name='admin_create_movie_api'),
    path('api/admin/filmes/fetch-metadata/', api_views.fetch_movie_metadata_api, name='fetch_movie_metadata_api'),
    path('api/admin/filmes/<int:movie_id>/deletar/', api_views.admin_delete_movie_api, name='admin_delete_movie_api'),
    
    # Categories API
    path('api/categorias/', api_views.categorias_api, name='categorias_api'),
    path('api/admin/categorias/criar/', api_views.admin_create_categoria_api, name='admin_create_categoria_api'),
    path('api/admin/categorias/<int:pk>/deletar/', api_views.admin_delete_categoria_api, name='admin_delete_categoria_api'),

    path('accounts/', include('django.contrib.auth.urls')),

    path('accounts/signup/', SignUpView.as_view(), name='signup'),

    path('api/auth/', include('clientes.api.urls'))
]
