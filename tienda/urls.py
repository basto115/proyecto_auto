
from django.urls import path
from . import views


urlpatterns = [
<<<<<<< Updated upstream
    path('', views.home, name="home"),
    path('', views.lista_productos, name='lista_productos'),
]
=======
    path('', views.lista_productos, name='lista_productos'),
]
>>>>>>> Stashed changes
