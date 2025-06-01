
from django.urls import path
from . import views
from .views import realizar_pedido
from .views import login_view


urlpatterns = [
    path('', views.home, name="home"),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('blog', views.blog, name="blog"),
    path('login', views.login, name="login"),
    path('checkout', views.checkout, name="checkout"),
    path('confirmation', views.confirmation, name="confirmation"),
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
    path('checkout/', views.checkout, name='checkout'),
    path('confirmacion/', views.confirmacion_pago, name='confirmacion_pago'),
    path('pedidos-bodeguero/', views.pedidos_bodeguero, name='pedidos_bodeguero'),
    path('pedidos-bodeguero/<int:pedido_id>/recolectado/', views.marcar_recolectado, name='marcar_recolectado'),
    path('pedidos-repartidor/', views.pedidos_repartidor, name='pedidos_repartidor'),
    path('pedidos-repartidor/<int:pedido_id>/entregado/', views.marcar_entregado, name='marcar_entregado'),
    path('pedidos/bodeguero/', views.pedidos_bodeguero, name='pedidos_bodeguero'),
    path('pedidos/bodeguero/<int:pedido_id>/recolectado/', views.marcar_recolectado, name='marcar_recolectado'),
    path('pedidos/repartidor/', views.pedidos_repartidor, name='pedidos_repartidor'),
    path('pedidos/repartidor/<int:pedido_id>/entregado/', views.marcar_entregado, name='marcar_entregado'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('<str:seccion>/', views.catalogo_por_seccion, name='catalogo_por_seccion'),
]
