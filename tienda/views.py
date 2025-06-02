from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Producto, Pedido, PedidoProducto, CustomUser
import requests
from django.contrib import messages
from .forms import PedidoForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Producto, Categoria
from django.urls import reverse
import mercadopago
from django.conf import settings
from django.contrib.auth.decorators import login_required
import json
from django.contrib.auth import authenticate, login, get_user_model,logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserRegisterSerializer, ProductoSerializer, PedidoSerializer, PedidoHistorialSerializer, ComprobanteTransferenciaSerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from functools import wraps
# Create your views here.

def home(request):
    productos_destacados = Producto.objects.filter(activo=True, destacado=True)[:8]
    return render(request, 'tienda/home.html', {'productos': productos_destacados})

def catalogo(request):
    categoria_id = request.GET.get('categoria')

    if categoria_id:
        productos = Producto.objects.filter(categoria_id=categoria_id, activo=True)
    else:
        productos = Producto.objects.filter(activo=True)

    categorias = Categoria.objects.all()
    modo_b2b = request.user.is_authenticated and request.user.is_b2b

    return render(request, 'tienda/catalogo.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': int(categoria_id) if categoria_id else None,
        'modo_b2b': modo_b2b
    })


def agregar_producto(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto = get_object_or_404(Producto, id=producto_id)
    
    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] += 1
    else:
        carrito[str(producto_id)] = {
            'nombre': producto.nombre,
            'precio': float(producto.precio_unitario),
            'cantidad': 1,
        }
        
    request.session['carrito'] = carrito
    messages.success(request, f"✅ {producto.nombre} fue añadido al carrito.")
    return redirect('catalogo')

def ver_carrito(request):
    carrito = request.session.get('carrito', {})

    # Calculamos subtotal por producto
    for item in carrito.values():
        item['subtotal'] = item['precio'] * item['cantidad']

    total = sum(item['subtotal'] for item in carrito.values())

    return render(request, 'tienda/carrito.html', {'carrito': carrito, 'total': total})

def eliminar_producto(request, producto_id):
    carrito = request.session.get('carrito', {})
    carrito.pop(str(producto_id), None)
    request.session['carrito'] = carrito
    return redirect('ver_carrito')

def vaciar_carrito(request):
    request.session['carrito'] = {}
    return redirect('ver_carrito')

def checkout(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        return redirect('ver_carrito')

    preference_items = []
    for id, item in carrito.items():
        preference_items.append({
            "title": item['nombre'],
            "quantity": int(item['cantidad']),
            "currency_id": "CLP",
            "unit_price": float(item['precio']),
        })

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    preference_data = {
        "items": preference_items,
        "back_urls": {
            "success": request.build_absolute_uri(reverse('confirmacion_pago')),
            "failure": request.build_absolute_uri(reverse('ver_carrito')),
            "pending": request.build_absolute_uri(reverse('ver_carrito')),
        },
    }

    preference_response = sdk.preference().create(preference_data)
    response_data = preference_response.get("response", {})

    if "init_point" in response_data:
        return render(request, 'tienda/checkout.html', {
        'carrito': carrito,
        'init_point': response_data["init_point"],
        'preference_id': response_data.get("id")
    })
    else:
        error = response_data.get("message", "No se pudo generar la preferencia de pago.")
        return render(request, 'tienda/checkout_error.html', {"error": error, "detalles": response_data})

def confirmacion_pago(request):
    request.session['carrito'] = {}  
    return render(request, 'tienda/confirmacion.html')

def confirmation(request):
    return render(request, 'tienda/confirmation.html')

def single_product(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    return render(request, 'tienda/single_product.html', {'producto': producto})

def blog(request):
    return render(request, 'tienda/blog.html')

def single_blog(request):
    return render(request, 'tienda/single_blog.html')


def tracking(request):
    return render(request, 'tienda/tracking.html')

def contact(request):
    return render(request, 'tienda/contact.html')


def realizar_pedido(request):
    productos_json = "[]"
    carrito = request.session.get("carrito", {})
    return render(request, 'tienda/realizar_pedido.html', {'productos_json': productos_json})


@login_required
def pedidos_bodeguero(request):
    pedidos = Pedido.objects.filter(estado='pagado')
    return render(request, 'tienda/pedidos_bodeguero.html', {'pedidos': pedidos})

@login_required
def marcar_recolectado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if pedido.estado == 'pagado':
        pedido.estado = 'recolectado'
        pedido.save()
    return redirect('pedidos_bodeguero')

@login_required
def pedidos_repartidor(request):
    pedidos = Pedido.objects.filter(estado='recolectado')
    return render(request, 'tienda/pedidos_repartidor.html', {'pedidos': pedidos})

@login_required
def marcar_entregado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if pedido.estado == 'recolectado':
        pedido.estado = 'entregado'
        pedido.save()
    return redirect('pedidos_repartidor')



def pedidos_bodeguero(request):
    pedidos = Pedido.objects.filter(estado='recolectando')
    return render(request, 'tienda/pedidos_bodeguero.html', {'pedidos': pedidos})

def marcar_recolectado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = 'recolectado'
    pedido.save()
    return redirect('pedidos_bodeguero')

def pedidos_repartidor(request):
    pedidos = Pedido.objects.filter(estado='recolectado')
    return render(request, 'tienda/pedidos_repartidor.html', {'pedidos': pedidos})

def marcar_entregado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = 'entregado'
    pedido.save()
    return redirect('pedidos_repartidor')

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'tienda/detalle_producto.html', {'producto': producto})

def realizar_pedido(request):
    productos_json = "[]"
    carrito = request.session.get("carrito", {})
    # Convertir los productos del carrito en JSON compatible con la API
    if carrito:
        productos_json = json.dumps([
            {
                "codigo_producto": item.get("codigo", ""),
                "cantidad": item.get("cantidad", 1)
            }
            for item in carrito.values()
        ])

    # Si se envía el formulario (POST)
    if request.method == 'POST':
        cliente_id = request.user.id
        tipo_entrega = request.POST.get('tipo_entrega')
        direccion = request.POST.get('direccion_entrega')
        productos = request.POST.get('productos')

        data = {
            "cliente_id": int(cliente_id),
            "productos": json.loads(productos),
            "tipo_entrega": tipo_entrega,
            "direccion_entrega": direccion
        }

        try:
            response = requests.post(
                'http://localhost:8000/api/orders',
                json=data,
                headers={'Authorization': f'Bearer {request.session.get("token", "")}'}
            )
            if response.status_code in [200, 201]:
                # Vaciar carrito después de pedido exitoso
                request.session['carrito'] = {}
                messages.success(request, 'Pedido realizado con éxito.')
                return redirect('checkout')
            else:
                messages.error(request, f"Error al registrar pedido: {response.status_code} - {response.text}")
        except Exception as e:
            messages.error(request, f"Error al conectar con la API: {str(e)}")
            
            

    return render(request, 'tienda/realizar_pedido.html', {
        'productos_json': productos_json,
    })


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Importante: si estás usando email como username
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # Redirige a donde quieras después de iniciar sesión
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')

    return render(request, 'tienda/login.html')



def catalogo_por_seccion(request, seccion):
    categorias_nombres = SECCIONES.get(seccion.lower(), [])
    filtro_nombre = request.GET.get('categoria')

    if filtro_nombre and filtro_nombre in categorias_nombres:
        productos = Producto.objects.filter(categoria__nombre=filtro_nombre, activo=True)
    else:
        productos = Producto.objects.filter(categoria__nombre__in=categorias_nombres, activo=True)

    return render(request, 'tienda/catalogo.html', {
        'productos': productos,
        'categorias': categorias_nombres,
        'seccion': seccion.capitalize()
    })
    
SECCIONES = {
    'repuestos': ['Filtros de aire', 'Filtros de aceite', 'Bujías', 'Correas de distribución'],
    'frenos': ['Pastillas de freno', 'Discos de freno', 'Amortiguadores', 'Rótulas'],
    'electricidad': ['Alternadores', 'Baterías', 'Luces y faros', 'Sensores y fusibles'],
    'accesorios': ['Alarmas', 'Cinturones de seguridad', 'Cubre asientos', 'Kits de emergencia'],
}

User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        rut = request.POST.get('rut')
        telefono = request.POST.get('telefono')
        is_b2b_raw = request.POST.get('is_b2b')
        is_b2b = is_b2b_raw in ['true', 'True', 'on', '1']

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Este email ya está registrado.")
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password1,
                is_b2b=is_b2b,
                nombre=nombre,
                apellido=apellido,
                rut=rut,
                telefono=telefono,
            )
            login(request, user)
            return redirect('home')

    return render(request, 'tienda/register.html')



def logout_view(request):
    logout(request)
    return redirect('home')  # O donde quieras redirigir

class RegisterUserView(APIView):
    def post(self, request):
        serializer = CustomUserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'Usuario registrado correctamente.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductoDetailView(APIView):
    def get(self, request, id):
        try:
            producto = Producto.objects.get(id=id)
            serializer = ProductoSerializer(producto)
            return Response(serializer.data)
        except Producto.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)


class PedidosPorUsuarioView(APIView):
    def get(self, request, user_id):
        pedidos = Pedido.objects.filter(cliente_id=user_id).order_by('-fecha_creacion')
        serializer = PedidoSerializer(pedidos, many=True)
        return Response(serializer.data)

class CrearPedidoPorEmailView(APIView):
    def post(self, request):
        email = request.data.get('email')
        productos = request.data.get('productos', [])
        tipo_entrega = request.data.get('tipo_entrega')
        direccion_entrega = request.data.get('direccion_entrega', '')

        if not email or not productos or not tipo_entrega:
            return Response({'error': 'Faltan datos obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cliente = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Cliente no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        pedido = Pedido.objects.create(
            cliente=cliente,
            tipo_entrega=tipo_entrega,
            direccion_entrega=direccion_entrega
        )

        for item in productos:
            producto_id = item.get('id')
            cantidad = item.get('cantidad', 1)
            try:
                producto = Producto.objects.get(id=producto_id)
                PedidoProducto.objects.create(pedido=pedido, producto=producto, cantidad=cantidad)
            except Producto.DoesNotExist:
                continue

        return Response({'mensaje': 'Pedido creado exitosamente', 'pedido_id': pedido.id}, status=status.HTTP_201_CREATED)

class CrearPedidoPorIDView(APIView):
    def post(self, request):
        data = request.data

        try:
            cliente = get_object_or_404(CustomUser, id=data.get("cliente_id"))
            tipo_entrega = data.get("tipo_entrega")
            direccion_entrega = data.get("direccion_entrega", "No especificado")
            productos = data.get("productos", [])

            if not productos:
                return Response({"error": "No se han enviado productos"}, status=status.HTTP_400_BAD_REQUEST)

            pedido = Pedido.objects.create(
                cliente=cliente,
                tipo_entrega=tipo_entrega,
                direccion_entrega=direccion_entrega
            )

            for item in productos:
                codigo = item.get("codigo_producto")
                cantidad = item.get("cantidad", 1)
                producto = Producto.objects.filter(codigo_producto=codigo).first()

                if producto:
                    PedidoProducto.objects.create(pedido=pedido, producto=producto, cantidad=cantidad)
                else:
                    pedido.delete()
                    return Response({"error": f"Producto con código {codigo} no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"mensaje": "Pedido creado correctamente", "pedido_id": pedido.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductoDetalleView(RetrieveAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    lookup_field = 'id'
    
class HistorialPedidosView(APIView):
    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({'error': 'Se requiere el email del usuario'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            pedidos = Pedido.objects.filter(cliente=user).order_by('-fecha_creacion')
            serializer = PedidoHistorialSerializer(pedidos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

class ActualizarEstadoPedidoView(APIView):
    def put(self, request, pedido_id):
        nuevo_estado = request.data.get('estado')

        if not nuevo_estado:
            return Response({'error': 'Debe proporcionar el nuevo estado'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pedido = Pedido.objects.get(id=pedido_id)
            pedido.estado = nuevo_estado
            pedido.save()
            return Response({'mensaje': f'Estado del pedido actualizado a "{nuevo_estado}"'}, status=status.HTTP_200_OK)
        except Pedido.DoesNotExist:
            return Response({'error': 'Pedido no encontrado'}, status=status.HTTP_404_NOT_FOUND)

class SubirComprobanteView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pedido_id):
        try:
            pedido = Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist:
            return Response({"error": "Pedido no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ComprobanteTransferenciaSerializer(pedido, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"mensaje": "Comprobante subido correctamente"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PedidosPendientesView(APIView):
    def get(self, request):
        pedidos = Pedido.objects.filter(estado="pendiente").order_by("-fecha_creacion")
        data = []

        for pedido in pedidos:
            productos = PedidoProducto.objects.filter(pedido=pedido)
            productos_info = [
                {
                    "producto": prod.producto.nombre,
                    "cantidad": prod.cantidad
                } for prod in productos
            ]

            data.append({
                "pedido_id": pedido.id,
                "cliente": pedido.cliente.email,
                "tipo_entrega": pedido.tipo_entrega,
                "direccion_entrega": pedido.direccion_entrega,
                "fecha_creacion": pedido.fecha_creacion,
                "productos": productos_info
            })

        return Response(data, status=status.HTTP_200_OK)
    

def rol_requerido(rol_permitido):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response({'error': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

            if request.user.rol != rol_permitido:
                return Response({'error': f'Se requiere rol: {rol_permitido}'}, status=status.HTTP_403_FORBIDDEN)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

class B2BProductsView(APIView):
    def get(self, request):
        user = request.user

        if not user.is_authenticated:
            return Response({'error': 'Autenticación requerida'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_b2b:
            return Response({'error': 'Acceso restringido a distribuidores B2B'}, status=status.HTTP_403_FORBIDDEN)

        productos = Producto.objects.filter(activo=True)
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)
