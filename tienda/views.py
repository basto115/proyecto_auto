from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Producto
import requests
from django.contrib import messages
from .forms import PedidoForm

# Create your views here.

def home(request):
    return render(request, 'tienda/home.html')

def category(request):
    return render(request, 'tienda/category.html')

def checkout(request):
    return render(request, 'tienda/checkout.html')

def confirmation(request):
    return render(request, 'tienda/confirmation.html')

def single_product(request):
    return render(request, 'tienda/single_product.html')

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
