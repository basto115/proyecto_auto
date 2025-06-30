

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator

# Modelo de Usuario (CustomUser)
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_b2b = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    nombre = models.CharField(max_length=100, blank=True)
    apellido = models.CharField(max_length=100, blank=True)
    rut = models.CharField(max_length=12, blank=True)
    telefono = models.CharField(max_length=20, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    ROLES = [
    ('cliente', 'Cliente'),
    ('bodeguero', 'Bodeguero'),
    ('contador', 'Contador'),
    ('repartidor', 'Repartidor'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
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
    codigo_producto = models.CharField(max_length=100, unique=True, default="Sin código")
    marca = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_unitario = models.IntegerField(default=0)
    precio_mayorista = models.IntegerField(default=0)
    impuesto = models.IntegerField(default=0)
    stock_disponible = models.IntegerField(default=0)
    unidad_medida = models.CharField(max_length=50, default="unidad")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    autor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
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

    cliente = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tipo_entrega = models.CharField(max_length=50, choices=[('retiro', 'Retiro'), ('domicilio', 'Domicilio')])
    direccion_entrega = models.CharField(max_length=255, blank=True, null=True, default="No especificado")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='pendiente')

    payment_id = models.CharField(max_length=100, blank=True, null=True)
    collection_id = models.CharField(max_length=100, blank=True, null=True)

    # ✅ Campo para subir comprobante de transferencia
    comprobante_transferencia = models.FileField(
        upload_to='comprobantes/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente} - {self.estado}"

# Modelo de PedidoProducto (pedidos_pedidoproducto)
class PedidoProducto(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)  # Valor predeterminado

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} unidades"
    
