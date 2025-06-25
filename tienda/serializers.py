from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import Producto, Pedido, PedidoProducto
from django.conf import settings

User = get_user_model()

class CustomUserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'password', 'nombre', 'apellido', 'rut', 'telefono', 'is_b2b', 'token']

    def validate_email(self, value):
        dominios_produccion = ["@gmail.com", "@duocuc.cl", "@hotmail.com"]

        if not settings.DEBUG:
            if not any(value.endswith(d) for d in dominios_produccion):
                raise serializers.ValidationError("Solo se permiten correos de los siguientes dominios: gmail, hotmail.")

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value

    def validate_rut(self, value):
        import re
        pattern = r"^\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]$"
        if not re.match(pattern, value):
            raise serializers.ValidationError("El RUT debe tener formato válido. Ej: 12.345.678-5")

        if User.objects.filter(rut=value).exists():
            raise serializers.ValidationError("Este RUT ya está registrado.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            nombre=validated_data.get('nombre', ''),
            apellido=validated_data.get('apellido', ''),
            rut=validated_data.get('rut', ''),
            telefono=validated_data.get('telefono', ''),
            is_b2b=validated_data.get('is_b2b', False)
        )
        Token.objects.create(user=user)
        return user

    def get_token(self, obj):
        token = Token.objects.get(user=obj)
        return token.key



class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'codigo_producto', 'marca', 'nombre', 'precio_mayorista', 'stock_disponible', 'unidad_medida', 'descripcion']
        
class PedidoProductoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_codigo = serializers.CharField(source='producto.codigo_producto', read_only=True)

    class Meta:
        model = PedidoProducto
        fields = ['producto_nombre', 'producto_codigo', 'cantidad']
        
class PedidoSerializer(serializers.ModelSerializer):
    productos = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = ['id', 'tipo_entrega', 'direccion_entrega', 'fecha_creacion', 'estado', 'productos']

    def get_productos(self, obj):
        productos = PedidoProducto.objects.filter(pedido=obj).select_related('producto')
        return PedidoProductoSerializer(productos, many=True).data

class PedidoHistorialSerializer(serializers.ModelSerializer):
    productos = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = ['id', 'fecha_creacion', 'estado', 'tipo_entrega', 'direccion_entrega', 'productos']

    def get_productos(self, obj):
        items = PedidoProducto.objects.filter(pedido=obj)
        return PedidoProductoSerializer(items, many=True).data

class ComprobanteTransferenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['comprobante_transferencia']
        
class PedidoDetalleSerializer(serializers.ModelSerializer):
    productos = serializers.SerializerMethodField()
    cliente_email = serializers.EmailField(source='cliente.email', read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_rut = serializers.CharField(source='cliente.rut', read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'cliente_nombre', 'cliente_rut', 'cliente_email', 'fecha_creacion', 'estado', 'tipo_entrega', 'direccion_entrega', 'productos']

    def get_productos(self, obj):
        productos = PedidoProducto.objects.filter(pedido=obj).select_related('producto')
        return PedidoProductoSerializer(productos, many=True).data