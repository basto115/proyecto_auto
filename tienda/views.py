from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Producto
import requests
from django.contrib import messages
from .forms import PedidoForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Producto, Categoria

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
    return redirect('catalogo')

def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
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
    return render(request, 'tienda/checkout.html')

def confirmation(request):
    return render(request, 'tienda/confirmation.html')

def single_product(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    return render(request, 'tienda/single_product.html', {'producto': producto})

def cart(request):
    return render(request, 'tienda/cart.html')

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
