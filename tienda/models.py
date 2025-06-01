

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# Modelo de Usuario (CustomUser)
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_b2b = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    groups = models.ManyToManyField('auth.Group', related_name='customuser_groups', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='customuser_permissions', blank=True)

    def __str__(self):
        return self.email


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

# Modelo de Producto (productos_producto)
class Producto(models.Model):
    codigo_producto = models.CharField(max_length=100, unique=True, default="Sin código")  # Valor predeterminado
    marca = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Valor predeterminado
    precio_mayorista = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Valor predeterminado
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Valor predeterminado
    stock_disponible = models.IntegerField(default=0)  # Valor predeterminado
    unidad_medida = models.CharField(max_length=50, default="unidad")  # Valor predeterminado
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Relación con el autor (usuario)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)
    destacado = models.BooleanField(default=False)
    
    def __str__(self):
        return self.nombre


# Modelo de Pedido (pedidos_pedido)
class Pedido(models.Model):
    ESTADOS_PEDIDO = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('recolectando', 'Recolectando productos'),
        ('recolectado', 'Productos recolectados'),
        ('en_reparto', 'En reparto'),
        ('entregado', 'Entregado'),
    ]
    
    cliente = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Relación con el cliente (usuario)
    tipo_entrega = models.CharField(max_length=50, choices=[('retiro', 'Retiro'), ('domicilio', 'Domicilio')])
    direccion_entrega = models.CharField(max_length=255, blank=True, null=True, default="No especificado")  # Valor predeterminado
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='pendiente')

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente} - {self.estado}"


# Modelo de PedidoProducto (pedidos_pedidoproducto)
class PedidoProducto(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)  # Valor predeterminado

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} unidades"
