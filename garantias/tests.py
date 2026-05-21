from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import (
    FormularioCliente,
    FormularioDiagnostico,
    FormularioEntrega,
    FormularioEvidencia,
    FormularioGarantia,
    FormularioVenta,
)
from .models import (
    CasoReparacion,
    CategoriaProducto,
    Cliente,
    Diagnostico,
    Entrega,
    EstadoCaso,
    Evidencia,
    Garantia,
    HistorialEstado,
    Producto,
    Venta,
)


class BasePruebasGarantias(TestCase):
    def crear_usuario(self, usuario, grupo=None, superusuario=False):
        if superusuario:
            return User.objects.create_superuser(
                username=usuario,
                password='clave-segura',
                email=f'{usuario}@example.com',
            )
        cuenta = User.objects.create_user(username=usuario, password='clave-segura')
        if grupo:
            cuenta.groups.add(Group.objects.get(name=grupo))
        return cuenta

    def crear_datos_base(self):
        categoria, _ = CategoriaProducto.objects.get_or_create(nombre='Computadores portatiles')
        cliente = Cliente.objects.create(
            tipo_documento='CC',
            documento='123456789',
            nombre='Laura Martinez',
            telefono='3001234567',
            correo='laura.martinez@example.com',
            direccion='Calle 80 #12-45',
            ciudad='Bogota',
        )
        producto = Producto.objects.create(
            nombre='Portatil',
            marca='Lenovo',
            modelo='ThinkPad E14',
            serial='LEN-E14-0001',
            categoria=categoria,
            descripcion='Portatil corporativo con cargador original.',
        )
        venta = Venta.objects.create(
            cliente=cliente,
            producto=producto,
            fecha_venta=date.today() - timedelta(days=30),
            valor=2500000,
            numero_factura='FAC-PRUEBA-001',
            observaciones='Venta con garantia registrada.',
        )
        garantia = Garantia.objects.create(
            venta=venta,
            fecha_inicio=venta.fecha_venta,
            fecha_fin=venta.fecha_venta + timedelta(days=365),
            estado='vigente',
            condiciones='Cubre defectos de fabricacion.',
        )
        estado_recibido = EstadoCaso.objects.get(codigo='recibido')
        caso = CasoReparacion.objects.create(
            garantia=garantia,
            descripcion_falla='El equipo no enciende al presionar el boton.',
            estado_actual=estado_recibido,
            prioridad='alta',
            fecha_ingreso=timezone.now() - timedelta(days=3),
            tecnico_responsable='Carlos Mesa',
            observaciones='Equipo recibido con cargador original.',
        )
        diagnostico = Diagnostico.objects.create(
            caso=caso,
            tecnico='Carlos Mesa',
            diagnostico='Se detecta falla en circuito de carga.',
            solucion='Reemplazar conector de carga.',
            requiere_repuesto=True,
            costo_estimado=85000,
            fecha=caso.fecha_ingreso + timedelta(hours=5),
        )
        evidencia = Evidencia.objects.create(
            caso=caso,
            tipo='ingreso',
            imagen='evidencias/pruebas/equipo_ingreso.jpg',
            descripcion='Foto del equipo al ingreso.',
            fecha=caso.fecha_ingreso + timedelta(minutes=20),
        )
        historial = HistorialEstado.objects.create(
            caso=caso,
            estado=estado_recibido,
            fecha=caso.fecha_ingreso,
            comentario='Caso recibido por recepcion.',
        )
        entrega = Entrega.objects.create(
            caso=caso,
            fecha_entrega=caso.fecha_ingreso + timedelta(days=4),
            entregado_a=cliente.nombre,
            documento_entrega=cliente.documento,
            recibido_conforme=True,
            observaciones='Producto revisado y recibido conforme.',
        )
        return {
            'categoria': categoria,
            'cliente': cliente,
            'producto': producto,
            'venta': venta,
            'garantia': garantia,
            'caso': caso,
            'diagnostico': diagnostico,
            'evidencia': evidencia,
            'historial': historial,
            'entrega': entrega,
        }


class PruebasModelosGarantias(BasePruebasGarantias):
    def setUp(self):
        self.datos = self.crear_datos_base()

    def test_catalogos_iniciales_existen(self):
        self.assertTrue(EstadoCaso.objects.filter(codigo='recibido').exists())
        self.assertTrue(EstadoCaso.objects.filter(es_final=True).exists())
        self.assertTrue(Group.objects.filter(name='Administrador').exists())
        self.assertTrue(Group.objects.filter(name='Recepcion').exists())
        self.assertTrue(Group.objects.filter(name='Tecnico').exists())
        self.assertTrue(Group.objects.filter(name='Consulta').exists())

    def test_garantia_fecha_fin_debe_ser_posterior(self):
        garantia = Garantia(
            venta=self.datos['venta'],
            fecha_inicio=date.today(),
            fecha_fin=date.today() - timedelta(days=1),
            estado='vigente',
        )
        with self.assertRaises(ValidationError):
            garantia.full_clean()

    def test_garantia_no_puede_iniciar_antes_de_venta(self):
        garantia = self.datos['garantia']
        garantia.fecha_inicio = self.datos['venta'].fecha_venta - timedelta(days=1)
        garantia.fecha_fin = self.datos['venta'].fecha_venta + timedelta(days=30)
        with self.assertRaises(ValidationError):
            garantia.full_clean()

    def test_caso_no_puede_cerrar_antes_de_ingreso(self):
        caso = self.datos['caso']
        caso.fecha_cierre = caso.fecha_ingreso - timedelta(hours=1)
        with self.assertRaises(ValidationError):
            caso.full_clean()

    def test_caso_no_permite_garantia_anulada(self):
        garantia = self.datos['garantia']
        garantia.estado = 'anulada'
        garantia.save()
        caso = CasoReparacion(
            garantia=garantia,
            descripcion_falla='No carga bateria.',
            estado_actual=EstadoCaso.objects.get(codigo='recibido'),
            prioridad='media',
            fecha_ingreso=timezone.now(),
        )
        with self.assertRaises(ValidationError):
            caso.full_clean()

    def test_entrega_no_puede_ser_antes_de_ingreso(self):
        entrega = self.datos['entrega']
        entrega.fecha_entrega = self.datos['caso'].fecha_ingreso - timedelta(days=1)
        with self.assertRaises(ValidationError):
            entrega.full_clean()

    def test_evidencia_rechaza_extension_no_permitida(self):
        evidencia = Evidencia(
            caso=self.datos['caso'],
            tipo='ingreso',
            imagen='evidencias/archivo.exe',
            descripcion='Archivo incorrecto.',
            fecha=timezone.now(),
        )
        with self.assertRaises(ValidationError):
            evidencia.full_clean()


class PruebasFormulariosGarantias(BasePruebasGarantias):
    def setUp(self):
        self.datos = self.crear_datos_base()

    def test_formulario_cliente_rechaza_telefono_invalido(self):
        formulario = FormularioCliente(data={
            'tipo_documento': 'CC',
            'documento': '987654321',
            'nombre': 'Cliente Nuevo',
            'telefono': 'abc',
            'correo': 'cliente@example.com',
            'direccion': 'Carrera 10 #20-30',
            'ciudad': 'Cali',
            'activo': 'on',
        })
        self.assertFalse(formulario.is_valid())
        self.assertIn('telefono', formulario.errors)

    def test_formulario_venta_rechaza_valor_negativo(self):
        formulario = FormularioVenta(data={
            'cliente': self.datos['cliente'].id,
            'producto': self.datos['producto'].id,
            'fecha_venta': date.today(),
            'valor': '-1',
            'numero_factura': 'FAC-NEGATIVA',
            'observaciones': 'Valor incorrecto.',
        })
        self.assertFalse(formulario.is_valid())
        self.assertIn('valor', formulario.errors)

    def test_formulario_garantia_rechaza_fechas_invalidas(self):
        otra_categoria = self.datos['categoria']
        otro_producto = Producto.objects.create(
            nombre='Monitor',
            marca='LG',
            modelo='UltraGear',
            serial='LG-MON-0002',
            categoria=otra_categoria,
        )
        otra_venta = Venta.objects.create(
            cliente=self.datos['cliente'],
            producto=otro_producto,
            fecha_venta=date.today(),
            valor=900000,
            numero_factura='FAC-GARANTIA-002',
        )
        formulario = FormularioGarantia(data={
            'venta': otra_venta.id,
            'fecha_inicio': date.today(),
            'fecha_fin': date.today() - timedelta(days=1),
            'estado': 'vigente',
            'condiciones': 'Condiciones comerciales.',
        })
        self.assertFalse(formulario.is_valid())
        self.assertIn('fecha_fin', formulario.errors)

    def test_formulario_diagnostico_rechaza_costo_negativo(self):
        formulario = FormularioDiagnostico(data={
            'caso': self.datos['caso'].id,
            'tecnico': 'Carlos Mesa',
            'diagnostico': 'Falla en puerto.',
            'solucion': 'Cambio de puerto.',
            'requiere_repuesto': 'on',
            'costo_estimado': '-100',
            'fecha': timezone.now().strftime('%Y-%m-%dT%H:%M'),
        })
        self.assertFalse(formulario.is_valid())
        self.assertIn('costo_estimado', formulario.errors)

    def test_formulario_evidencia_rechaza_extension_invalida(self):
        archivo = SimpleUploadedFile('soporte.exe', b'contenido', content_type='application/octet-stream')
        formulario = FormularioEvidencia(
            data={
                'caso': self.datos['caso'].id,
                'tipo': 'ingreso',
                'descripcion': 'Archivo incorrecto.',
                'fecha': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            },
            files={'imagen': archivo},
        )
        self.assertFalse(formulario.is_valid())
        self.assertIn('imagen', formulario.errors)

    def test_formulario_entrega_rechaza_fecha_anterior_al_ingreso(self):
        otro_producto = Producto.objects.create(
            nombre='Tableta',
            marca='Samsung',
            modelo='Tab A9',
            serial='SAM-TAB-0003',
            categoria=self.datos['categoria'],
        )
        otra_venta = Venta.objects.create(
            cliente=self.datos['cliente'],
            producto=otro_producto,
            fecha_venta=date.today(),
            valor=700000,
            numero_factura='FAC-ENTREGA-003',
        )
        otra_garantia = Garantia.objects.create(
            venta=otra_venta,
            fecha_inicio=otra_venta.fecha_venta,
            fecha_fin=otra_venta.fecha_venta + timedelta(days=365),
            estado='vigente',
        )
        otro_caso = CasoReparacion.objects.create(
            garantia=otra_garantia,
            descripcion_falla='No conecta a WiFi.',
            estado_actual=EstadoCaso.objects.get(codigo='recibido'),
            fecha_ingreso=timezone.now(),
        )
        fecha_invalida = (otro_caso.fecha_ingreso - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        formulario = FormularioEntrega(data={
            'caso': otro_caso.id,
            'fecha_entrega': fecha_invalida,
            'entregado_a': 'Laura Martinez',
            'documento_entrega': '123456789',
            'recibido_conforme': 'on',
            'observaciones': 'Fecha incorrecta.',
        })
        self.assertFalse(formulario.is_valid())
        self.assertIn('fecha_entrega', formulario.errors)


class PruebasPermisosYVistas(BasePruebasGarantias):
    def setUp(self):
        self.datos = self.crear_datos_base()
        self.superadmin = self.crear_usuario('superadmin', superusuario=True)
        self.administrador = self.crear_usuario('administrador', grupo='Administrador')
        self.recepcionista = self.crear_usuario('recepcion', grupo='Recepcion')
        self.tecnico = self.crear_usuario('tecnico', grupo='Tecnico')
        self.consulta = self.crear_usuario('consulta', grupo='Consulta')
        self.sin_rol = self.crear_usuario('sinrol')

    def test_usuario_sin_ingresar_es_redirigido_al_login(self):
        respuesta = self.client.get(reverse('dashboard'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse('login'), respuesta.url)

    def test_usuario_sin_rol_recibe_403(self):
        self.client.force_login(self.sin_rol)
        respuesta = self.client.get(reverse('dashboard'))
        self.assertEqual(respuesta.status_code, 403)

    def test_administrador_puede_ver_todas_las_listas(self):
        self.client.force_login(self.administrador)
        nombres = [
            'dashboard',
            'cliente_list',
            'categoria_list',
            'producto_list',
            'venta_list',
            'garantia_list',
            'caso_list',
            'diagnostico_list',
            'evidencia_list',
            'estado_list',
            'historial_list',
            'entrega_list',
        ]
        for nombre in nombres:
            with self.subTest(nombre=nombre):
                respuesta = self.client.get(reverse(nombre))
                self.assertEqual(respuesta.status_code, 200)

    def test_detalles_responden_para_administrador(self):
        self.client.force_login(self.administrador)
        rutas = [
            ('cliente_detail', self.datos['cliente'].id),
            ('categoria_detail', self.datos['categoria'].id),
            ('producto_detail', self.datos['producto'].id),
            ('venta_detail', self.datos['venta'].id),
            ('garantia_detail', self.datos['garantia'].id),
            ('caso_detail', self.datos['caso'].id),
            ('diagnostico_detail', self.datos['diagnostico'].id),
            ('evidencia_detail', self.datos['evidencia'].id),
            ('estado_detail', EstadoCaso.objects.get(codigo='recibido').id),
            ('historial_detail', self.datos['historial'].id),
            ('entrega_detail', self.datos['entrega'].id),
        ]
        for nombre, identificador in rutas:
            with self.subTest(nombre=nombre):
                respuesta = self.client.get(reverse(nombre, kwargs={'pk': identificador}))
                self.assertEqual(respuesta.status_code, 200)

    def test_formularios_de_creacion_responden_segun_rol_correcto(self):
        casos = [
            (self.recepcionista, 'cliente_create', 200),
            (self.recepcionista, 'producto_create', 200),
            (self.recepcionista, 'venta_create', 200),
            (self.recepcionista, 'garantia_create', 200),
            (self.recepcionista, 'caso_create', 200),
            (self.recepcionista, 'evidencia_create', 200),
            (self.recepcionista, 'entrega_create', 200),
            (self.tecnico, 'diagnostico_create', 200),
            (self.tecnico, 'historial_create', 200),
            (self.consulta, 'cliente_create', 403),
            (self.tecnico, 'venta_create', 403),
            (self.recepcionista, 'estado_create', 403),
        ]
        for usuario, nombre_url, codigo in casos:
            with self.subTest(usuario=usuario.username, nombre_url=nombre_url):
                self.client.force_login(usuario)
                respuesta = self.client.get(reverse(nombre_url))
                self.assertEqual(respuesta.status_code, codigo)

    def test_recepcion_no_puede_entrar_a_estados(self):
        self.client.force_login(self.recepcionista)
        respuesta = self.client.get(reverse('estado_list'))
        self.assertEqual(respuesta.status_code, 403)

    def test_tecnico_puede_diagnosticos_pero_no_ventas(self):
        self.client.force_login(self.tecnico)
        respuesta_diagnosticos = self.client.get(reverse('diagnostico_list'))
        respuesta_ventas = self.client.get(reverse('venta_list'))
        self.assertEqual(respuesta_diagnosticos.status_code, 200)
        self.assertEqual(respuesta_ventas.status_code, 403)

    def test_consulta_ve_listas_pero_no_crea(self):
        self.client.force_login(self.consulta)
        self.assertEqual(self.client.get(reverse('caso_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('diagnostico_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('caso_create')).status_code, 403)

    def test_tecnico_puede_avanzar_estado_y_recepcion_no(self):
        caso = self.datos['caso']
        self.client.force_login(self.recepcionista)
        respuesta_bloqueada = self.client.get(reverse('caso_avanzar', kwargs={'caso_id': caso.id}))
        self.assertEqual(respuesta_bloqueada.status_code, 403)

        self.client.force_login(self.tecnico)
        estado_anterior = caso.estado_actual_id
        respuesta = self.client.get(reverse('caso_avanzar', kwargs={'caso_id': caso.id}))
        caso.refresh_from_db()
        self.assertEqual(respuesta.status_code, 302)
        self.assertNotEqual(caso.estado_actual_id, estado_anterior)
        self.assertTrue(HistorialEstado.objects.filter(caso=caso, comentario='Avance rapido de estado.').exists())

    def test_post_crea_cliente_con_recepcion(self):
        self.client.force_login(self.recepcionista)
        respuesta = self.client.post(reverse('cliente_create'), data={
            'tipo_documento': 'CC',
            'documento': '555444333',
            'nombre': 'Andres Rojas',
            'telefono': '3109876543',
            'correo': 'andres.rojas@example.com',
            'direccion': 'Carrera 45 #10-20',
            'ciudad': 'Medellin',
            'activo': 'on',
        })
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(Cliente.objects.filter(documento='555444333').exists())

    def test_busqueda_en_lista_clientes(self):
        self.client.force_login(self.administrador)
        respuesta = self.client.get(reverse('cliente_list'), {'q': 'Laura'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Laura Martinez')


class PruebasComandoCargaDatos(TestCase):
    def test_comando_carga_datos_reales_crea_relaciones(self):
        from django.core.management import call_command

        call_command('cargar_datos_reales', cantidad=12, limpiar=True, verbosity=0)
        self.assertEqual(Cliente.objects.count(), 12)
        self.assertEqual(Producto.objects.count(), 12)
        self.assertEqual(Venta.objects.count(), 12)
        self.assertEqual(Garantia.objects.count(), 12)
        self.assertEqual(CasoReparacion.objects.count(), 12)
        self.assertEqual(Diagnostico.objects.count(), 12)
        self.assertEqual(Evidencia.objects.count(), 12)
        self.assertEqual(HistorialEstado.objects.count(), 12)
        self.assertEqual(Entrega.objects.count(), 12)
        self.assertTrue(CasoReparacion.objects.select_related('garantia__venta__cliente').exists())
