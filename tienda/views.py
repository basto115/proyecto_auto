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