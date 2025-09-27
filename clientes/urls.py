from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.client_list, name='list'),
    path('search/', views.client_search, name='search'),
    path('create/', views.client_create, name='create'),
    path('<int:client_id>/', views.client_detail, name='detail'),
    path('<int:client_id>/edit/', views.client_update, name='update'),
    path('<int:client_id>/delete/', views.client_delete, name='delete'),
]

