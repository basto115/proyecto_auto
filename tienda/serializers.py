from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import Producto, Pedido, PedidoProducto

User = get_user_model()

class CustomUserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'password', 'nombre', 'apellido', 'rut', 'telefono', 'is_b2b', 'token']

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
        fields = '__all__'
        
class PedidoProductoSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer()

    class Meta:
        model = PedidoProducto
        fields = ['producto', 'cantidad']
        
class PedidoSerializer(serializers.ModelSerializer):
    productos = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = ['id', 'tipo_entrega', 'direccion_entrega', 'fecha_creacion', 'estado', 'productos']

    def get_productos(self, obj):
        productos = PedidoProducto.objects.filter(pedido=obj).select_related('producto')
        return PedidoProductoSerializer(productos, many=True).data