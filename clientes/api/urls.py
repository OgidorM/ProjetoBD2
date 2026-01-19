from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.ClienteSignupView.as_view(), name='cliente_signup'),
    path('login/', views.ClienteLoginView.as_view(), name='cliente_login'),
    path('me/', views.ClienteMeView.as_view(), name='cliente_me'),
]