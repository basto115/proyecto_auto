from django.contrib import admin

from .models import CustomUser, Producto, Pedido, PedidoProducto

admin.site.register(CustomUser)
admin.site.register(Producto)
admin.site.register(Pedido)
admin.site.register(PedidoProducto)
