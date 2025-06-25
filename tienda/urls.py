
from django.urls import path
from . import views
from .views import realizar_pedido, login_view, register_view, logout_view, RegisterUserView, PedidosPorUsuarioView, CrearPedidoPorEmailView, CrearPedidoPorIDView, GenerarCotizacionPDF, ProductoListView
from .views import ProductoDetalleView, HistorialPedidosView, ActualizarEstadoPedidoView, SubirComprobanteView, PedidosPendientesView, B2BProductsView, vista_distribuidores, PedidoDetalleView, LoginView, EmailTokenObtainPairView
from .views import CotizarEnvioChilexpressView, BuscarCalleGeoreferenciaChilexpressView
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView


urlpatterns = [
    path('', views.home, name="home"),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('blog/', views.blog, name="blog"),
    
    # HTML login (formulario web tradicional)
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


    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),

    # Bodeguero
    path('pedidos/bodeguero/', views.pedidos_bodeguero, name='pedidos_bodeguero'),
    path('pedidos/bodeguero/<int:pedido_id>/recolectado/', views.marcar_recolectado, name='marcar_recolectado'),

    # Repartidor
    path('pedidos/repartidor/', views.pedidos_repartidor, name='pedidos_repartidor'),
    path('pedidos/repartidor/<int:pedido_id>/entregado/', views.marcar_entregado, name='marcar_entregado'),
    path('logout/', logout_view, name='logout'),

    
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),

    
    path('api/register/', RegisterUserView.as_view(), name='api_register_user'),
    
    
    path('api/pedidos/usuario/<int:user_id>/', PedidosPorUsuarioView.as_view(), name='pedidos_usuario'),
    path('api/orders/', CrearPedidoPorIDView.as_view(), name='crear_pedido'),
    path('api/pedidos/crear/', CrearPedidoPorEmailView.as_view()),
    path('api/products/<int:id>/', ProductoDetalleView.as_view(), name='producto_detalle'),
    path('api/pedidos/historial/', HistorialPedidosView.as_view(), name='historial_pedidos'),
    path('api/pedidos/<int:pedido_id>/actualizar_estado/', ActualizarEstadoPedidoView.as_view(), name='actualizar_estado_pedido'),
    path('api/pedidos/<int:pedido_id>/subir_comprobante/', SubirComprobanteView.as_view(), name='subir_comprobante'),
    path('api/pedidos/pendientes/', PedidosPendientesView.as_view(), name='pedidos_pendientes'),
    path('api/b2b/products/', B2BProductsView.as_view(), name='b2b_products'),
    path('api/pedidos/<int:pedido_id>/', PedidoDetalleView.as_view(), name='detalle_pedido'),
    path('api/auth/login/', LoginView.as_view(), name='api_login'),
    path('api/pedidos/<int:pedido_id>/cotizacion_pdf/', GenerarCotizacionPDF.as_view(), name='cotizacion_pdf'),
    path('api/products/', ProductoListView.as_view(), name='lista_productos'),
    
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/login/', EmailTokenObtainPairView.as_view(), name='email_token_obtain_pair'),
    
    #chilexpress
    path('api/chilexpress/cotizar/', CotizarEnvioChilexpressView.as_view(), name='cotizar_envio'),

    path('distribuidores/', vista_distribuidores, name='vista_distribuidores'),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    
    path('<str:seccion>/', views.catalogo_por_seccion, name='catalogo_por_seccion'),
    path('chilexpress/calles/', BuscarCalleGeoreferenciaChilexpressView.as_view(), name='buscar-calles-chilexpress'),
    path('cotizacion/generar/', views.generar_cotizacion, name='generar_cotizacion'),
    

]

# se habian duplicado los urls lol
