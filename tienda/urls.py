
from django.urls import path
from . import views
from .views import realizar_pedido


urlpatterns = [
    path('', views.home, name="home"),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('checkout', views.checkout, name="checkout"),
    path('confirmation', views.confirmation, name="confirmation"),
    path('producto/<int:producto_id>/', views.single_product, name='single_product'),
    path('cart', views.cart, name="cart"),
    path('blog', views.blog, name="blog"),
    path('single_blog', views.single_blog, name="single_blog"),
    path('login', views.login, name="login"),
    path('tracking', views.tracking, name="tracking"),
    path('contact', views.contact, name="contact"),
    path('realizar-pedido/', realizar_pedido, name='realizar_pedido'),
    path('agregar/<int:producto_id>/', views.agregar_producto, name='agregar_producto'),
]
