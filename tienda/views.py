from django.shortcuts import render
from django.http import HttpResponse
from .models import Producto

<<<<<<< Updated upstream
# Create your views here.

def home(request):
    return render(request, 'tienda/index.html')
=======
from django.http import HttpResponse
from .models import Producto

def inicio(request):
    return HttpResponse("¡Bienvenido a AutoParts!")


>>>>>>> Stashed changes

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/lista_productos.html', {'productos': productos})
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
