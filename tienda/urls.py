
from django.urls import path
from . import views
from .views import realizar_pedido
from .views import login_view


urlpatterns = [
    path('', views.home, name="home"),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('checkout', views.checkout, name="checkout"),
    path('confirmation', views.confirmation, name="confirmation"),
    path('producto/<int:producto_id>/', views.single_product, name='single_product'),
    path('blog', views.blog, name="blog"),
    path('single_blog', views.single_blog, name="single_blog"),
    path('login/', login_view, name="login"),
    path('tracking', views.tracking, name="tracking"),
    path('contact', views.contact, name="contact"),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('realizar-pedido/', realizar_pedido, name='realizar_pedido'),
    path('agregar/<int:producto_id>/', views.agregar_producto, name='agregar_producto'),
    path('eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
]
