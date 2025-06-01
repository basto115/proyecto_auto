from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Producto, Pedido
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


# Create your views here.

def home(request):
    productos_destacados = Producto.objects.filter(activo=True, destacado=True)[:8]
    return render(request, 'tienda/home.html', {'productos': productos_destacados})

def catalogo(request):
    categoria_id = request.GET.get('categoria')
    categorias = Categoria.objects.all()

    if categoria_id:
        productos = Producto.objects.filter(activo=True, categoria_id=categoria_id)
    else:
        productos = Producto.objects.filter(activo=True)

    return render(request, 'tienda/catalogo.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_id': int(categoria_id) if categoria_id else None,
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
    total = 0

    for id, item in carrito.items():
        item['subtotal'] = item['precio'] * item['cantidad']
        total += item['subtotal']

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

def blog(request):
    return render(request, 'tienda/blog.html')

def single_blog(request):
    return render(request, 'tienda/single_blog.html')

def login(request):
    return render(request, 'tienda/login.html')

def tracking(request):
    return render(request, 'tienda/tracking.html')

def contact(request):
    return render(request, 'tienda/contact.html')


def realizar_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            data = {
                "cliente_id": form.cleaned_data['cliente_id'],
                "productos": eval(form.cleaned_data['productos']),  # debería venir como JSON string
                "tipo_entrega": form.cleaned_data['tipo_entrega'],
                "direccion_entrega": form.cleaned_data['direccion_entrega'],
            }
            try:
                response = requests.post(
                    'http://localhost:8000/api/orders',
                    json=data,
                    headers={'Authorization': f'Bearer {request.session.get("token")}'}
                )
                if response.status_code == 200 or response.status_code == 201:
                    messages.success(request, 'Pedido realizado con éxito.')
                    return redirect('catalogo')  # o cualquier vista que quieras
                else:
                    messages.error(request, f'Error: {response.status_code} - {response.text}')
            except Exception as e:
                messages.error(request, f'Error al contactar la API: {str(e)}')
    else:
        form = PedidoForm()

    return render(request, 'tienda/realizar_pedido.html', {'form': form})

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
