
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('', views.lista_productos, name='lista_productos'),
]
