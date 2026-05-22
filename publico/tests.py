from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from garantias.models import CasoReparacion, CategoriaProducto, Cliente, EstadoCaso, Garantia, Producto, Venta


class PruebasModuloPublico(TestCase):
    def setUp(self):
        categoria, _ = CategoriaProducto.objects.get_or_create(nombre='Computadores')
        cliente = Cliente.objects.create(
            tipo_documento='CC',
            documento='100200300',
            nombre='Cliente Publico',
            telefono='3001234567',
            correo='cliente.publico@example.com',
        )
        producto = Producto.objects.create(
            nombre='Portatil',
            marca='Dell',
            modelo='Inspiron',
            serial='PUB-001',
            categoria=categoria,
        )
        venta = Venta.objects.create(
            cliente=cliente,
            producto=producto,
            fecha_venta=date.today() - timedelta(days=20),
            valor=2200000,
            numero_factura='FAC-PUBLICA-001',
        )
        garantia = Garantia.objects.create(
            venta=venta,
            fecha_inicio=venta.fecha_venta,
            fecha_fin=venta.fecha_venta + timedelta(days=365),
            estado='vigente',
        )
        self.caso = CasoReparacion.objects.create(
            garantia=garantia,
            descripcion_falla='No enciende.',
            estado_actual=EstadoCaso.objects.get(codigo='recibido'),
            prioridad='alta',
            fecha_ingreso=timezone.now(),
            tecnico_responsable='Tecnico Garantias',
        )

    def test_inicio_publico_no_exige_login(self):
        respuesta = self.client.get(reverse('inicio_publico'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Garantias y reparaciones')
        self.assertContains(respuesta, 'favicon.svg')
        self.assertContains(respuesta, 'hero-garantias.png')
        self.assertContains(respuesta, 'numero-publico')

    def test_servicios_publicos_no_exige_login(self):
        respuesta = self.client.get(reverse('servicios_publicos'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Servicios orientados')
        self.assertContains(respuesta, 'servicios-garantias.png')

    def test_consulta_publica_encuentra_caso_por_factura(self):
        respuesta = self.client.get(reverse('consulta_estado_publico'), {
            'documento': '100200300',
            'codigo': 'FAC-PUBLICA-001',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'consulta-garantias.png')
        self.assertContains(respuesta, f'Caso #{self.caso.id}')
        self.assertContains(respuesta, 'Recibido')

    def test_consulta_publica_encuentra_caso_por_id(self):
        respuesta = self.client.get(reverse('consulta_estado_publico'), {
            'documento': '100200300',
            'codigo': str(self.caso.id),
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Cliente Publico')

    def test_consulta_publica_no_muestra_si_documento_no_coincide(self):
        respuesta = self.client.get(reverse('consulta_estado_publico'), {
            'documento': '999999999',
            'codigo': 'FAC-PUBLICA-001',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'No encontramos un caso')
