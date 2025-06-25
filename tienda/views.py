from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
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
from django.contrib.auth import authenticate, login, get_user_model, logout
User = get_user_model()
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserRegisterSerializer, ProductoSerializer, PedidoSerializer, PedidoHistorialSerializer, ComprobanteTransferenciaSerializer, PedidoDetalleSerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from functools import wraps
from django.db.models import Q
from .forms import CustomRegisterForm
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.templatetags.static import static




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
        'modo_b2b': modo_b2b,
        'mostrar_buscador' : True  
    })


def agregar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    cantidad = int(request.POST.get('cantidad', 1))

    if cantidad > producto.stock_disponible:
        messages.error(request, "No puedes agregar más unidades que el stock disponible.")
        return redirect(request.META.get('HTTP_REFERER', 'catalogo'))

    carrito = request.session.get('carrito', {})

    if request.user.is_authenticated and getattr(request.user, 'is_b2b', False):
        precio = int(producto.precio_mayorista)
    else:
        precio = int(producto.precio_unitario)

    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] += cantidad
    else:
        carrito[str(producto_id)] = {
            'nombre': producto.nombre,
            'precio': precio,
            'cantidad': cantidad,
        }

    request.session['carrito'] = carrito
    messages.success(request, f"✅ {cantidad} unidad(es) de {producto.nombre} añadida(s) al carrito.")
    return redirect(request.META.get('HTTP_REFERER', 'catalogo'))


def ver_carrito(request):
    carrito = request.session.get('carrito', {})


    for item in carrito.values():
        item['subtotal'] = int(item['precio']) * item['cantidad']

    total = sum(int(item['subtotal']) for item in carrito.values())

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
            "unit_price": int(item['precio']),
        })

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    domain = "https://autoparts.pythonanywhere.com"

    preference_data = {
        "items": preference_items,
        "back_urls": {
            "success": domain + reverse('confirmation'),
            "failure": domain + reverse('ver_carrito'),
            "pending": domain + reverse('ver_carrito'),
        },
        "auto_return": "approved"
    }

    preference_response = sdk.preference().create(preference_data)
    response_data = preference_response.get("response", {})
    
    productos = []
    for item in carrito.values():
        productos.append({
            "nombre": item["nombre"],
            "precio": int(item["precio"]),
            "cantidad": int(item["cantidad"])
        })
    productos_json = json.dumps(productos)

    if "init_point" in response_data:
        return render(request, 'tienda/checkout.html', {
            'carrito': carrito,
            'init_point': response_data["init_point"],
            'preference_id': response_data.get("id"),
            'productos_json': productos_json
        })
    else:
        error = response_data.get("message", "No se pudo generar la preferencia de pago.")
        return render(request, 'tienda/checkout_error.html', {"error": error, "detalles": response_data})



def confirmation(request):
    request.session['carrito'] = {}  
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
    pedidos = Pedido.objects.filter(estado__in=['pagado', 'recolectando'])
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

    if request.user.is_authenticated and request.user.is_b2b:
        precio = producto.precio_mayorista
        modo_b2b = True
    else:
        precio = producto.precio_unitario
        modo_b2b = False

    return render(request, 'tienda/detalle_producto.html', {
        'producto': producto,
        'precio': precio,
        'modo_b2b': modo_b2b,
    })


def realizar_pedido(request):
    productos_json = "[]"
    carrito = request.session.get("carrito", {})
    
    if carrito:
        productos_json = json.dumps([
            {
                "codigo_producto": item.get("codigo", ""),
                "cantidad": item.get("cantidad", 1)
            }
            for item in carrito.values()
        ])


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


        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
        
            #token
            from rest_framework.authtoken.models import Token
            token, _ = Token.objects.get_or_create(user=user)
            request.session['token'] = token.key 

            return redirect('home')
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

    modo_b2b = request.user.is_authenticated and request.user.is_b2b

    return render(request, 'tienda/catalogo.html', {
        'productos': productos,
        'categorias': categorias_nombres,
        'modo_b2b': modo_b2b,
        'seccion': seccion.capitalize(),
        'mostrar_buscador' : True
    })
    
SECCIONES = {
    'repuestos': ['Filtros de aire', 'Filtros de aceite', 'Bujías', 'Correas de distribución'],
    'frenos': ['Pastillas de freno', 'Discos de freno', 'Amortiguadores', 'Rótulas'],
    'electricidad': ['Alternadores', 'Baterías', 'Luces y faros', 'Sensores y fusibles'],
    'accesorios': ['Alarmas', 'Cinturones de seguridad', 'Cubre asientos', 'Kits de emergencia'],
}

User = get_user_model()

from .forms import CustomRegisterForm

def register_view(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data['email'],
                email=data['email'],
                password=data['password1'],
                is_b2b=data['is_b2b'],
                nombre=data['nombre'],
                apellido=data['apellido'],
                rut=data['rut'],
                telefono=data['telefono'],
            )
            login(request, user)
            return redirect('home')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = CustomRegisterForm()

    return render(request, 'tienda/register.html', {'form': form})




def logout_view(request):
    logout(request)
    return redirect('home')  

class RegisterUserView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = CustomUserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'Usuario registrado correctamente.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



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
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication]  
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
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request, pedido_id):
        nuevo_estado = request.data.get('estado')

        if not nuevo_estado:
            return Response({'error': 'Debe proporcionar el nuevo estado'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Validar estado permitido
        estados_validos = [opcion[0] for opcion in Pedido.ESTADOS_PEDIDO]
        if nuevo_estado not in estados_validos:
            return Response({'error': 'Estado inválido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pedido = Pedido.objects.get(id=pedido_id)
            
        except Pedido.DoesNotExist:
            return Response({'error': 'Pedido no encontrado'}, status=status.HTTP_404_NOT_FOUND)


        if not request.user.is_staff:
            return Response({'error': 'No tienes permisos para actualizar el estado'}, status=status.HTTP_403_FORBIDDEN)

        pedido.estado = nuevo_estado
        pedido.save()
        return Response({'mensaje': f'Estado del pedido actualizado a "{nuevo_estado}"'}, status=status.HTTP_200_OK)

class SubirComprobanteView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, pedido_id):
        try:
            pedido = Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist:
            return Response({"error": "Pedido no encontrado"}, status=404)

        if pedido.cliente != request.user:
            return Response({"error": "No autorizado para modificar este pedido"}, status=403)

        archivo = request.FILES.get("comprobante")
        if not archivo:
            return Response({"error": "Archivo requerido"}, status=400)

        pedido.comprobante_transferencia = archivo
        pedido.save()

        return Response({"mensaje": "Comprobante subido correctamente"}, status=200)
    
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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not getattr(request.user, 'is_b2b', False):
            return Response({'error': 'Acceso restringido a distribuidores B2B'}, status=status.HTTP_403_FORBIDDEN)

        productos = Producto.objects.filter(activo=True)
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)

def vista_distribuidores(request):
    if not request.user.is_authenticated or not request.user.is_b2b:
        return redirect('login')

    productos = Producto.objects.filter(precio_mayorista__gt=0, activo=True)
    return render(request, 'tienda/productos_b2b.html', {
        'productos': productos,
        'modo_b2b': True,
    })

def buscar_productos(request):
    query = request.GET.get('q')
    resultados = Producto.objects.filter(
        Q(nombre__icontains=query) | Q(descripcion__icontains=query)
    )
    return render(request, 'tienda/buscar_resultados.html', {
        'resultados': resultados,
        'query': query,
    })

        
class PedidoDetalleView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pedido_id):
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            serializer = PedidoDetalleSerializer(pedido)
            return Response(serializer.data)
        except Pedido.DoesNotExist:
            return Response({'error': 'Pedido no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
class LoginView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
        
class GenerarCotizacionPDF(APIView):
    permission_classes = [IsAuthenticated]

class GenerarCotizacionPDF(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pedido_id):
        try:
            pedido = Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist:
            raise Http404("Pedido no encontrado")

        if request.user != pedido.cliente and not request.user.is_staff:
            return Response({'error': 'No autorizado'}, status=403)

        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="cotizacion_pedido_{pedido.id}.pdf"'

        
        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter
        y = height - 50

        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, f"Cotización Pedido #{pedido.id}")
        y -= 30

        p.setFont("Helvetica", 12)
        p.drawString(50, y, f"Cliente: {pedido.cliente.nombre}")
        y -= 20
        p.drawString(50, y, f"RUT: {pedido.cliente.rut}")
        y -= 20
        p.drawString(50, y, f"Email: {pedido.cliente.email}")
        y -= 30
        p.drawString(50, y, f"Tipo de Entrega: {pedido.tipo_entrega}")
        y -= 20
        p.drawString(50, y, f"Dirección: {pedido.direccion_entrega}")
        y -= 30

        p.drawString(50, y, "Productos:")
        y -= 20

        total = 0
        for detalle in pedido.pedidoproducto_set.all():
            subtotal = detalle.cantidad * detalle.producto.precio_unitario
            total += subtotal
            linea = f"- {detalle.producto.nombre}  ({detalle.cantidad} x ${detalle.producto.precio_unitario:,}) = ${subtotal:,}"
            p.drawString(60, y, linea)
            y -= 20
            if y < 100:  
                p.showPage()
                y = height - 50

        y -= 10
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y - 10, f"Total: ${total:,}")
        p.showPage()
        p.save()

        return response

class ProductoListView(ListAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [AllowAny] 
    

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email inválido")

        if not user.check_password(password):
            raise serializers.ValidationError("Contraseña incorrecta")

        data = super().validate({"username": user.username, "password": password})
        return data


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    
class CotizarEnvioChilexpressView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        payload = {
            "originCountyCode": data.get("origen"),
            "destinationCountyCode": data.get("destino"),
            "package": {
                "weight": data.get("peso"),
                "height": data.get("alto"),
                "width": data.get("ancho"),
                "length": data.get("largo")
            },
            "productType": data.get("producto", 3),
            "contentReference": data.get("referencia", "Cotización AutoParts")
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Ocp-Apim-Subscription-Key": settings.CHILEXPRESS_COTIZAR_API_KEY
        }

        try:
            url = "http://testservices.wschilexpress.com/rating/api/v1/rates/courier"
            response = requests.post(url, json=payload, headers=headers)
            return Response(response.json(), status=response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BuscarCalleGeoreferenciaChilexpressView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        nombre = request.GET.get("name")
        limit = request.GET.get("limit", 10)

        if not nombre:
            return Response({"error": "Parámetro 'name' requerido."}, status=400)

        url = "http://testservices.wschilexpress.com/georeference/api/v1/streets/search"
        params = {
            "name": nombre,
            "limit": limit
        }
        headers = {
            "Accept": "application/json",
            "Ocp-Apim-Subscription-Key": settings.CHILEXPRESS_GEOREF_API_KEY
        }

        try:
            response = requests.get(url, headers=headers, params=params)

            
            print("URL solicitada a Chilexpress:", response.url)
            print("Status Code:", response.status_code)
            print("Respuesta:", response.text)

            return Response(response.json(), status=response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

def generar_cotizacion(request):
    if request.method == 'POST':
        mano_obra = int(request.POST.get('mano_obra', 0))
        productos_json = request.POST.get('productos_json', '[]')
        productos = json.loads(productos_json)

        total_productos = sum(p['precio'] * p['cantidad'] for p in productos)
        total_final = total_productos + mano_obra
        logo_path = request.build_absolute_uri(static('img/logo_auto.png'))

        context = {
            'productos': productos,
            'mano_obra': mano_obra,
            'total_productos': total_productos,
            'total_final': total_final,
            'cliente': request.user,
            'logo_path': logo_path
        }

        template = get_template('tienda/cotizacion_pdf.html')
        html = template.render(context)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="cotizacion.pdf"'
        pisa.CreatePDF(html, dest=response)
        return response
    
    