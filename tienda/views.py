from django.shortcuts import render
from django.http import HttpResponse
from .models import Producto

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
