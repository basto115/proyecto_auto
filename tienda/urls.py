
from django.urls import path
from . import views
from .views import realizar_pedido, login_view, register_view, logout_view, RegisterUserView, ProductoDetailView, PedidosPorUsuarioView, CrearPedidoPorEmailView, CrearPedidoPorIDView
from .views import ProductoDetalleView, HistorialPedidosView, ActualizarEstadoPedidoView, SubirComprobanteView, PedidosPendientesView, B2BProductsView

urlpatterns = [
    path('', views.home, name="home"),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('blog/', views.blog, name="blog"),
    path('login/', login_view, name="login"),
    path('register/', register_view, name='register'),
    path('checkout/', views.checkout, name="checkout"),
    path('confirmation/', views.confirmation, name="confirmation"),
    path('single_blog/', views.single_blog, name="single_blog"),
    path('tracking/', views.tracking, name="tracking"),
    path('contact/', views.contact, name="contact"),

    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('realizar-pedido/', realizar_pedido, name='realizar_pedido'),
    path('agregar/<int:producto_id>/', views.agregar_producto, name='agregar_producto'),
    path('eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('vaciar/', views.vaciar_carrito, name='vaciar_carrito'),

    path('confirmacion/', views.confirmacion_pago, name='confirmacion_pago'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),

    # Bodeguero
    path('pedidos/bodeguero/', views.pedidos_bodeguero, name='pedidos_bodeguero'),
    path('pedidos/bodeguero/<int:pedido_id>/recolectado/', views.marcar_recolectado, name='marcar_recolectado'),

    # Repartidor
    path('pedidos/repartidor/', views.pedidos_repartidor, name='pedidos_repartidor'),
    path('pedidos/repartidor/<int:pedido_id>/entregado/', views.marcar_entregado, name='marcar_entregado'),
    path('logout/', logout_view, name='logout'),

    
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('<str:seccion>/', views.catalogo_por_seccion, name='catalogo_por_seccion'),
    
    path('api/register/', RegisterUserView.as_view(), name='api_register_user'),
    path('api/products/<int:id>/', ProductoDetailView.as_view(), name='producto_detail'),
    path('api/pedidos/usuario/<int:user_id>/', PedidosPorUsuarioView.as_view(), name='pedidos_usuario'),
    path('api/orders/', CrearPedidoPorIDView.as_view()),
    path('api/pedidos/crear/', CrearPedidoPorEmailView.as_view()),
    path('api/products/<int:id>/', ProductoDetalleView.as_view(), name='producto_detalle'),
    path('api/pedidos/historial/', HistorialPedidosView.as_view(), name='historial_pedidos'),
    path('api/pedidos/<int:pedido_id>/actualizar_estado/', ActualizarEstadoPedidoView.as_view(), name='actualizar_estado_pedido'),
    path('api/pedidos/<int:pedido_id>/subir_comprobante/', SubirComprobanteView.as_view(), name='subir_comprobante'),
    path('api/pedidos/pendientes/', PedidosPendientesView.as_view(), name='pedidos_pendientes'),
    path('api/b2b/products', B2BProductsView.as_view(), name='b2b_products'),
]

# se habian duplicado los urls lol
