from django.shortcuts import render
from django.http import HttpResponse
from .models import Producto

# Create your views here.

def home(request):
    return render(request, 'tienda/index.html')

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/lista_productos.html', {'productos': productos})

