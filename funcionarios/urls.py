from django.urls import path
from . import views

app_name = 'funcionarios'

urlpatterns = [
    path('', views.employee_list, name='list'),
    path('search/', views.employee_search, name='search'),
    path('create/', views.employee_create, name='create'),
    path('<int:employee_id>/', views.employee_detail, name='detail'),
    path('<int:employee_id>/edit/', views.employee_update, name='update'),
    path('<int:employee_id>/delete/', views.employee_delete, name='delete'),
]

