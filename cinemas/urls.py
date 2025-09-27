from django.urls import path
from . import views

app_name = 'cinemas'

urlpatterns = [
    path('', views.cinema_list, name='list'),
    path('search/', views.cinema_search, name='search'),
    path('create/', views.cinema_create, name='create'),
    path('<int:cinema_id>/', views.cinema_detail, name='detail'),
    path('<int:cinema_id>/edit/', views.cinema_update, name='update'),
    path('<int:cinema_id>/delete/', views.cinema_delete, name='delete'),
]

