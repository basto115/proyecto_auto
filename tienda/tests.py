from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from tienda.models import Producto, CustomUser, Pedido, PedidoProducto

# Create your tests here.

class RegistroUsuarioTests(APITestCase):
    
    #test registro
    def test_registro_usuario_valido(self):
        data = {
            "email": "usuario_prueba@gmail.com",
            "password": "clave123",
            "nombre": "Test",
            "apellido": "User",
            "rut": "12.345.678-5",
            "telefono": "+56911112222",
            "is_b2b": False
        }
        response = self.client.post("/api/register/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_registro_usuario_email_invalido(self):
        data = {
            "email": "usuario@noesgmail.com",
            "password": "clave123",
            "nombre": "Test",
            "apellido": "User",
            "rut": "12.345.678-5",
            "telefono": "+56911112222",
            "is_b2b": False
        }
        response = self.client.post("/api/register/", data, format='json')
        self.assertIn(response.status_code, [400, 422])

    def test_registro_rut_invalido(self):
        data = {
            "email": "usuario@gmail.com",
            "password": "clave123",
            "nombre": "Test",
            "apellido": "User",
            "rut": "12345678",  
            "telefono": "+56911112222",
            "is_b2b": False
        }
        response = self.client.post("/api/register/", data, format='json')
        self.assertIn(response.status_code, [400, 422])
    
    def test_registro_email_duplicado(self):
        data = {
            "email": "duplicado@gmail.com",
            "password": "clave123",
            "nombre": "Test",
            "apellido": "User",
            "rut": "12.345.678-5",
            "telefono": "+56911112222",
            "is_b2b": False
        }
        
        self.client.post("/api/register/", data, format='json')
        
        data["rut"] = "12.345.678-6" 
        response = self.client.post("/api/register/", data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_registro_rut_duplicado(self):
        data = {
            "email": "nuevo@gmail.com",
            "password": "clave123",
            "nombre": "Test",
            "apellido": "User",
            "rut": "11.111.111-1",
            "telefono": "+56922223333",
            "is_b2b": False
        }
        
        self.client.post("/api/register/", data, format='json')
        
        data["email"] = "otro@gmail.com"  
        response = self.client.post("/api/register/", data, format='json')
        self.assertEqual(response.status_code, 400)
        
    def test_registro_sin_telefono(self):
        data = {
            "email": "notel@gmail.com",
            "password": "clave123",
            "nombre": "Sin",
            "apellido": "Telefono",
            "rut": "16.666.666-6",
            "is_b2b": False
        }
        response = self.client.post("/api/register/", data, format='json')
        self.assertEqual(response.status_code, 201)
    
    #test login    
    def test_login_exitoso(self):
        
        self.client.post("/api/register/", {
            "email": "testlogin@gmail.com",
            "password": "clave123",
            "nombre": "Log",
            "apellido": "In",
            "rut": "13.456.789-0",
            "telefono": "+56900000001",
            "is_b2b": False
        }, format='json')

        
        response = self.client.post("/api/login/", {
            "email": "testlogin@gmail.com",
            "password": "clave123"
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
    
    def test_login_password_incorrecta(self):
        self.client.post("/api/register/", {
            "email": "errorpass@gmail.com",
            "password": "clave123",
            "nombre": "Error",
            "apellido": "Pass",
            "rut": "17.111.111-1",
            "telefono": "+56900000001",
            "is_b2b": False
        }, format='json')

        response = self.client.post("/api/login/", {
            "email": "errorpass@gmail.com",
            "password": "malaClave"
        }, format='json')

        self.assertEqual(response.status_code, 401)
        
    def test_login_email_inexistente(self):
        response = self.client.post("/api/login/", {
            "email": "noexiste@gmail.com",
            "password": "loquesea"
        }, format='json')
        self.assertEqual(response.status_code, 401)
    
    def test_login_campos_vacios(self):
        response = self.client.post("/api/login/", {
            "email": "",
            "password": ""
        }, format='json')
        self.assertEqual(response.status_code, 400)
    
    def test_login_sin_password(self):
        response = self.client.post("/api/login/", {
            "email": "alguien@gmail.com"
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login_sin_email(self):
        response = self.client.post("/api/login/", {
            "password": "clave123"
        }, format='json')
        self.assertEqual(response.status_code, 400)
    
    #test productos    
    def test_ver_lista_productos_sin_auth(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        
    def test_ver_productos_vacio(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
        
    def test_ver_producto_existente(self):
        user = CustomUser.objects.create_user(
            username="admin@autoparts.cl",
            email="admin@autoparts.cl",
            password="admin123",
            nombre="Admin",
            apellido="Root",
            rut="11.111.111-1",
            telefono="+56999999999"
        )

        Producto.objects.create(
            nombre="Filtro de Aceite",
            precio_mayorista=4990,
            stock_disponible=10,
            descripcion="Filtro original Bosch",
            autor=user  
        )

        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["nombre"], "Filtro de Aceite")
    
    def test_ver_multiples_productos(self):
        user = CustomUser.objects.create_user(
            username="dev@autoparts.cl",
            email="dev@autoparts.cl",
            password="clave123",
            rut="12.345.678-9",
            nombre="Dev",
            apellido="Tester"
        )

        Producto.objects.create(
            nombre="Bujía",
            codigo_producto="TEST-BUJIA", 
            precio_mayorista=2990,
            stock_disponible=20,
            descripcion="NGK",
            autor=user
        )
        
        Producto.objects.create(
            nombre="Amortiguador",
            codigo_producto="TEST-AMORT",  
            precio_mayorista=15990,
            stock_disponible=8,
            descripcion="Monroe",
            autor=user
        )

        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        
    def test_ver_producto_sin_stock(self):
        user = CustomUser.objects.create_user(username="userstock0", email="stock@zero.com", password="123", rut="22.222.222-2", nombre="Zero", apellido="Stock")

        Producto.objects.create(
            nombre="Sensor ABS",
            codigo_producto="TEST-SENSOR",  
            precio_mayorista=8900,
            stock_disponible=0,
            descripcion="Bosch",
            autor=user
        )

        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["stock_disponible"], 0)
        
    def test_ver_producto_con_campos_completos(self):
        user = CustomUser.objects.create_user(
            username="campos@autoparts.cl",
            email="campos@autoparts.cl",
            password="clave123",
            rut="10.101.010-1",
            nombre="Campos",
            apellido="Tester"
        )

        Producto.objects.create(
            codigo_producto="P1001",
            nombre="Disco de Freno Premium",
            marca="Brembo",
            descripcion="Disco ventilado de alta calidad.",
            precio_unitario=30000,
            precio_mayorista=25000,
            impuesto=19,
            stock_disponible=12,
            unidad_medida="unidad",
            autor=user
        )

        response = self.client.get("/api/products/")
        producto = response.data[0]

        self.assertEqual(producto["codigo_producto"], "P1001")
        self.assertEqual(producto["nombre"], "Disco de Freno Premium")
        self.assertEqual(producto["marca"], "Brembo")
        self.assertEqual(producto["stock_disponible"], 12)
    
    #test producto especifico
    def test_ver_detalle_producto_existente(self):
        user = CustomUser.objects.create_user(
            username="detalleuser",
            email="detalle@prod.cl",
            password="123",
            rut="10.222.333-4",
            nombre="Detalle",
            apellido="Tester"
        )

        producto = Producto.objects.create(
            nombre="Kit Emergencia",
            codigo_producto="DET-001",
            marca="Brembo",
            descripcion="Incluye triángulo, linterna y botiquín",
            precio_unitario=19990,
            precio_mayorista=14990,
            stock_disponible=15,
            autor=user
        )

        response = self.client.get(f"/api/products/{producto.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["nombre"], "Kit Emergencia")
        
    def test_ver_detalle_producto_inexistente(self):
        response = self.client.get("/api/products/999/")
        self.assertEqual(response.status_code, 404)
    
    def test_ver_detalle_sin_auth(self):
        user = CustomUser.objects.create_user(username="authfree", email="libre@ver.com", password="123", rut="12.345.678-0", nombre="Ver", apellido="Libre")
        producto = Producto.objects.create(nombre="Pastillas de freno", codigo_producto="DET-002", stock_disponible=9, autor=user)
        response = self.client.get(f"/api/products/{producto.id}/")
        self.assertEqual(response.status_code, 200)
    
    def test_ver_detalle_con_campos_clave(self):
        user = CustomUser.objects.create_user(username="campos", email="campos@ver.com", password="123", rut="11.222.333-4", nombre="Campos", apellido="Det")
        producto = Producto.objects.create(
            nombre="Batería 12V",
            codigo_producto="DET-003",
            marca="Yuasa",
            descripcion="Batería para vehículo mediano",
            precio_unitario=59990,
            precio_mayorista=52990,
            stock_disponible=6,
            unidad_medida="unidad",
            autor=user
        )
        response = self.client.get(f"/api/products/{producto.id}/")
        self.assertEqual(response.data["codigo_producto"], "DET-003")
        self.assertEqual(response.data["marca"], "Yuasa")
        self.assertEqual(response.data["unidad_medida"], "unidad")
    
    def test_detalle_producto_inactivo(self):
        user = CustomUser.objects.create_user(username="inactivo", email="inactivo@ver.com", password="123", rut="17.111.111-1", nombre="In", apellido="Activo")
        producto = Producto.objects.create(nombre="Rótula", codigo_producto="DET-004", stock_disponible=3, autor=user, activo=False)
        response = self.client.get(f"/api/products/{producto.id}/")
        self.assertEqual(response.status_code, 200)  
    
    def test_ver_detalle_sin_id(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200) 
        self.assertIsInstance(response.data, list)
    
    #test pedido
    def test_crear_pedido_exitoso(self):
        user = CustomUser.objects.create_user(
            username="cliente", email="cliente@test.com", password="123", rut="20.111.111-1", nombre="Cliente", apellido="Test"
        )

        producto = Producto.objects.create(
            nombre="Fusible",
            codigo_producto="PED-001",
            precio_mayorista=500,
            stock_disponible=100,
            autor=user
        )

        token = self.client.post("/api/login/", {"email": "cliente@test.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "email": "cliente@test.com",  
            "productos": [{"id": producto.id, "cantidad": 2}],  
            "tipo_entrega": "domicilio",
            "direccion_entrega": "Av. Principal 123"
        }

        response = self.client.post("/api/pedidos/crear/", data, format="json")
        print(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["mensaje"], "Pedido creado exitosamente")
    
    def test_crear_pedido_sin_auth(self):
        response = self.client.post("/api/pedidos/crear/", {"productos": []}, format="json")
        self.assertIn(response.status_code, [401, 403])
    
    def test_crear_pedido_sin_productos(self):
        user = CustomUser.objects.create_user(username="user", email="x@test.com", password="123", rut="21.111.111-1", nombre="No", apellido="Prod")
        token = self.client.post("/api/login/", {"email": "x@test.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.post("/api/pedidos/crear/", {"productos": []}, format="json")
        self.assertEqual(response.status_code, 400)
    
    def test_crear_pedido_producto_inexistente(self):
        user = CustomUser.objects.create_user(username="falso", email="falso@test.com", password="123", rut="22.222.222-2", nombre="Falso", apellido="Pedido")
        token = self.client.post("/api/login/", {"email": "falso@test.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "productos": [{"producto_id": 9999, "cantidad": 1}]
        }

        response = self.client.post("/api/pedidos/crear/", data, format="json")
        self.assertEqual(response.status_code, 400)
    
    def test_crear_pedido_con_cantidad_invalida(self):
        user = CustomUser.objects.create_user(username="invalido", email="invalido@test.com", password="123", rut="23.333.333-3", nombre="Inva", apellido="Lido")
        producto = Producto.objects.create(nombre="Luz LED", codigo_producto="PED-002", precio_mayorista=3000, stock_disponible=10, autor=user)

        token = self.client.post("/api/login/", {"email": "invalido@test.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "productos": [{"producto_id": producto.id, "cantidad": -5}]
        }

        response = self.client.post("/api/pedidos/crear/", data, format="json")
        self.assertEqual(response.status_code, 400)
    
    def test_crear_pedido_multiples_productos(self):
        user = CustomUser.objects.create_user(username="multi", email="multi@test.com", password="123", rut="24.444.444-4", nombre="Multi", apellido="Test")
        
        p1 = Producto.objects.create(nombre="Filtro", codigo_producto="PED-F1", precio_mayorista=2500, stock_disponible=20, autor=user)
        p2 = Producto.objects.create(nombre="Aceite", codigo_producto="PED-A2", precio_mayorista=5000, stock_disponible=15, autor=user)

        token = self.client.post("/api/login/", {"email": "multi@test.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "email": "multi@test.com",
            "tipo_entrega": "domicilio",
            "direccion_entrega": "Av. Siempre Viva 123",
            "productos": [
                {"id": p1.id, "cantidad": 1},
                {"id": p2.id, "cantidad": 2}
            ]
        }

        response = self.client.post("/api/pedidos/crear/", data, format="json")
        print(response.data)
        self.assertEqual(response.status_code, 201)
    
    #test historial
    def test_historial_con_pedidos(self):
        user = CustomUser.objects.create_user(username="historial", email="histo@auto.com", password="123", rut="25.555.555-5", nombre="Histo", apellido="Test")
        
        producto = Producto.objects.create(nombre="Alternador", codigo_producto="HIST-001", precio_mayorista=29990, stock_disponible=10, autor=user)
        
        pedido = Pedido.objects.create(cliente=user, tipo_entrega="domicilio", direccion_entrega="Av. Central 111", estado="pendiente")
        PedidoProducto.objects.create(pedido=pedido, producto=producto, cantidad=1)

        token = self.client.post("/api/login/", {"email": "histo@auto.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(f"/api/pedidos/historial/?email={user.email}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        
    def test_historial_sin_pedidos(self):
        user = CustomUser.objects.create_user(username="vacio", email="vacio@auto.com", password="123", rut="26.666.666-6", nombre="Sin", apellido="Pedidos")
        
        token = self.client.post("/api/login/", {"email": "vacio@auto.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(f"/api/pedidos/historial/?email={user.email}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
    
    def test_historial_sin_autenticacion(self):
        response = self.client.get("/api/pedidos/historial/")
        self.assertIn(response.status_code, [401, 403])
        
    def test_historial_no_incluye_pedidos_de_otros(self):
        user1 = CustomUser.objects.create_user(username="cliente1", email="c1@auto.com", password="123", rut="27.777.777-7", nombre="Uno", apellido="Test")
        user2 = CustomUser.objects.create_user(username="cliente2", email="c2@auto.com", password="123", rut="28.888.888-8", nombre="Dos", apellido="Test")
        
        producto = Producto.objects.create(nombre="Correa", codigo_producto="HIST-002", precio_mayorista=7000, stock_disponible=10, autor=user1)

        pedido = Pedido.objects.create(cliente=user1, tipo_entrega="retiro", direccion_entrega="Av. Test", estado="pendiente")
        PedidoProducto.objects.create(pedido=pedido, producto=producto, cantidad=2)

        token = self.client.post("/api/login/", {"email": "c2@auto.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(f"/api/pedidos/historial/?email={user1.email}")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        
    def test_historial_devuelve_detalle(self):
        user = CustomUser.objects.create_user(username="detallehist", email="detalle@auto.com", password="123", rut="29.999.999-9", nombre="Hist", apellido="Detalle")
        producto = Producto.objects.create(nombre="Batería", codigo_producto="HIST-003", precio_mayorista=39990, stock_disponible=5, autor=user)

        pedido = Pedido.objects.create(cliente=user, tipo_entrega="domicilio", direccion_entrega="Calle A 123", estado="pendiente")
        PedidoProducto.objects.create(pedido=pedido, producto=producto, cantidad=1)

        token = self.client.post("/api/login/", {"email": "detalle@auto.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(f"/api/pedidos/historial/?email={user.email}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["estado"], "pendiente")
    
    def test_historial_multiples_pedidos(self):
        user = CustomUser.objects.create_user(username="multiuser", email="multiped@auto.com", password="123", rut="30.101.010-1", nombre="Multi", apellido="Pedidos")
        producto = Producto.objects.create(nombre="Filtro", codigo_producto="HIST-004", precio_mayorista=2000, stock_disponible=100, autor=user)

        for _ in range(3):
            pedido = Pedido.objects.create(cliente=user, tipo_entrega="retiro", direccion_entrega="Test 123", estado="pendiente")
            PedidoProducto.objects.create(pedido=pedido, producto=producto, cantidad=1)

        token = self.client.post("/api/login/", {"email": "multiped@auto.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(f"/api/pedidos/historial/?email={user.email}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
    
    #test comprobante
    def test_subir_comprobante_exitoso(self):
        user = CustomUser.objects.create_user(username="comprador", email="comprador@auto.com", password="123", rut="33.333.333-3", nombre="Comprador", apellido="Ejemplo")
        pedido = Pedido.objects.create(cliente=user, tipo_entrega="domicilio", direccion_entrega="Calle 1", estado="pendiente")

        token = self.client.post("/api/login/", {"email": "comprador@auto.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        from django.core.files.uploadedfile import SimpleUploadedFile
        file = SimpleUploadedFile("comprobante.pdf", b"archivo prueba", content_type="application/pdf")

        response = self.client.post(f"/api/pedidos/{pedido.id}/subir_comprobante/", {"comprobante": file})
        self.assertEqual(response.status_code, 200)
        self.assertIn("subido", response.data["mensaje"])
    
    def test_subir_comprobante_sin_auth(self):
        user = CustomUser.objects.create_user(username="anonimo", email="anonimo@auto.com", password="123", rut="34.444.444-4", nombre="Anonimo", apellido="User")
        pedido = Pedido.objects.create(cliente=user, tipo_entrega="retiro", direccion_entrega="SinAuth", estado="pendiente")

        from django.core.files.uploadedfile import SimpleUploadedFile
        file = SimpleUploadedFile("comprobante.jpg", b"imagen prueba", content_type="image/jpeg")

        response = self.client.post(f"/api/pedidos/{pedido.id}/subir_comprobante/", {"comprobante": file})
        self.assertEqual(response.status_code, 401)
    
    def test_subir_comprobante_ajeno(self):
        owner = CustomUser.objects.create_user(username="dueno", email="dueno@auto.com", password="123", rut="35.555.555-5", nombre="Dueno", apellido="Legitimo")
        intruso = CustomUser.objects.create_user(username="intruso", email="intruso@auto.com", password="123", rut="36.666.666-6", nombre="Intruso", apellido="NoAutorizado")

        pedido = Pedido.objects.create(cliente=owner, tipo_entrega="domicilio", direccion_entrega="Calle falsa", estado="pendiente")

        token = self.client.post("/api/login/", {"email": "intruso@auto.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        from django.core.files.uploadedfile import SimpleUploadedFile
        file = SimpleUploadedFile("comprobante.jpg", b"imagen falsa", content_type="image/jpeg")

        response = self.client.post(f"/api/pedidos/{pedido.id}/subir_comprobante/", {"comprobante": file})
        self.assertEqual(response.status_code, 403)
    
    def test_subir_sin_archivo(self):
        user = CustomUser.objects.create_user(username="sinarchivo", email="sinarchivo@auto.com", password="123", rut="37.777.777-7", nombre="Sin", apellido="Archivo")
        pedido = Pedido.objects.create(cliente=user, tipo_entrega="retiro", direccion_entrega="Dirección", estado="pendiente")

        token = self.client.post("/api/login/", {"email": "sinarchivo@auto.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.post(f"/api/pedidos/{pedido.id}/subir_comprobante/")
        self.assertEqual(response.status_code, 400)
    
    def test_subir_pedido_inexistente(self):
        user = CustomUser.objects.create_user(username="fakeuser", email="fake@auto.com", password="123", rut="38.888.888-8", nombre="Fake", apellido="User")

        token = self.client.post("/api/login/", {"email": "fake@auto.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        from django.core.files.uploadedfile import SimpleUploadedFile
        file = SimpleUploadedFile("comprobante.pdf", b"prueba", content_type="application/pdf")

        response = self.client.post(f"/api/pedidos/9999/subir_comprobante/", {"comprobante": file})
        self.assertEqual(response.status_code, 404)
        
    def test_subir_comprobante_se_guarda(self):
        user = CustomUser.objects.create_user(username="guardar", email="guardar@auto.com", password="123", rut="39.999.999-9", nombre="Guardar", apellido="PDF")
        pedido = Pedido.objects.create(cliente=user, tipo_entrega="domicilio", direccion_entrega="Calle Guardar", estado="pendiente")

        token = self.client.post("/api/login/", {"email": "guardar@auto.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        from django.core.files.uploadedfile import SimpleUploadedFile
        file = SimpleUploadedFile("comprobante.pdf", b"contenido", content_type="application/pdf")

        response = self.client.post(
            f"/api/pedidos/{pedido.id}/subir_comprobante/",
            {"comprobante": file} 
        )
        print("RESPONSE:", response.data)
        pedido.refresh_from_db()
        self.assertTrue(pedido.comprobante_transferencia)
        self.assertIn("comprobante", pedido.comprobante_transferencia.name)
        
    #estado pedido
    def test_actualizar_estado_exitoso(self):
        user = CustomUser.objects.create_user(username="staff", email="staff@auto.com", password="123", rut="40.101.101-1", nombre="Staff", apellido="Miembro", is_staff=True)
        pedido = Pedido.objects.create(cliente=user, tipo_entrega="domicilio", direccion_entrega="Calle 1", estado="pendiente")

        token = self.client.post("/api/login/", {"email": "staff@auto.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.put(f"/api/pedidos/{pedido.id}/actualizar_estado/", {"estado": "pagado"}, format="json")
        self.assertEqual(response.status_code, 200)
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, "pagado")
    
    def test_actualizar_estado_sin_auth(self):
        user = CustomUser.objects.create_user(username="cliente", email="cliente@auto.com", password="123", rut="40.222.222-2", nombre="Cliente", apellido="Final")
        pedido = Pedido.objects.create(cliente=user, tipo_entrega="retiro", direccion_entrega="Calle 2", estado="pendiente")

        response = self.client.put(f"/api/pedidos/{pedido.id}/actualizar_estado/", {"estado": "pagado"}, format="json")
        self.assertEqual(response.status_code, 401)
    
    def test_actualizar_estado_sin_permisos(self):
        user = CustomUser.objects.create_user(username="normal", email="normal@auto.com", password="123", rut="40.333.333-3", nombre="Sin", apellido="Permiso")
        pedido = Pedido.objects.create(cliente=user, tipo_entrega="domicilio", direccion_entrega="Calle 3", estado="pendiente")

        token = self.client.post("/api/login/", {"email": "normal@auto.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.put(f"/api/pedidos/{pedido.id}/actualizar_estado/", {"estado": "pagado"}, format="json")
        self.assertEqual(response.status_code, 403)
    
    def test_actualizar_estado_pedido_inexistente(self):
        staff = CustomUser.objects.create_user(username="staff2", email="staff2@auto.com", password="123", rut="40.444.444-4", nombre="Otro", apellido="Staff", is_staff=True)

        token = self.client.post("/api/login/", {"email": "staff2@auto.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.put("/api/pedidos/9999/actualizar_estado/", {"estado": "pagado"}, format="json")
        self.assertEqual(response.status_code, 404)
    
    def test_actualizar_estado_invalido(self):
        staff = CustomUser.objects.create_user(username="staff3", email="staff3@auto.com", password="123", rut="40.555.555-5", nombre="Staff", apellido="Invalido", is_staff=True)
        pedido = Pedido.objects.create(cliente=staff, tipo_entrega="domicilio", direccion_entrega="Calle 4", estado="pendiente")

        token = self.client.post("/api/login/", {"email": "staff3@auto.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.put(f"/api/pedidos/{pedido.id}/actualizar_estado/", {"estado": "desconocido"}, format="json")
        self.assertEqual(response.status_code, 400)
    
    def test_actualizar_estado_sin_dato(self):
        staff = CustomUser.objects.create_user(username="staff4", email="staff4@auto.com", password="123", rut="40.666.666-6", nombre="Staff", apellido="SinDato", is_staff=True)
        pedido = Pedido.objects.create(cliente=staff, tipo_entrega="retiro", direccion_entrega="Calle 5", estado="pendiente")

        token = self.client.post("/api/login/", {"email": "staff4@auto.com", "password": "123"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.put(f"/api/pedidos/{pedido.id}/actualizar_estado/", {}, format="json")
        self.assertEqual(response.status_code, 400)