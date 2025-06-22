from django.contrib import admin
from .models import CustomUser, Producto, Pedido, PedidoProducto, Categoria

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_b2b', 'rol', 'date_joined']
    list_filter = ['is_b2b', 'rol']
    search_fields = ['email', 'nombre', 'apellido']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    readonly_fields = ['autor', 'fecha_creacion', 'fecha_actualizacion']

    def get_readonly_fields(self, request, obj=None):
        base_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            return base_fields + [
                'precio_unitario',
                'precio_mayorista',
                'impuesto',
                'stock_disponible'
            ]
        return base_fields

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.autor = request.user
        super().save_model(request, obj, form, change)

    def get_fields(self, request, obj=None):
        fields = [
            'nombre', 'codigo_producto', 'marca', 'descripcion',
            'precio_unitario', 'precio_mayorista', 'impuesto',
            'stock_disponible', 'unidad_medida', 'activo',
            'imagen', 'categoria', 'destacado',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        if obj:  
            fields.insert(fields.index('imagen'), 'autor')
        return fields

    list_display = [
        'nombre', 'autor', 'precio_unitario',
        'precio_mayorista', 'stock_disponible', 'fecha_actualizacion'
    ]
    list_filter = ['activo', 'categoria']
    search_fields = ['nombre', 'codigo_producto']
    
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    readonly_fields = ['fecha_creacion']
    list_display = ['id', 'cliente', 'estado', 'fecha_creacion']
    list_filter = ['estado']
    search_fields = ['cliente__email']

@admin.register(PedidoProducto)
class PedidoProductoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'producto', 'cantidad']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre']