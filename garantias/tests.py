from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import CategoriaProducto, Cliente, EstadoCaso, Garantia, Producto, Venta


class GarantiasModelTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            tipo_documento='CC',
            documento='123456',
            nombre='Cliente Demo',
            telefono='3001234567',
            correo='cliente@example.com',
        )
        self.categoria, _ = CategoriaProducto.objects.get_or_create(nombre='Celulares')
        self.producto = Producto.objects.create(
            nombre='Telefono',
            marca='Marca',
            modelo='X1',
            serial='SER-001',
            categoria=self.categoria,
        )
        self.venta = Venta.objects.create(
            cliente=self.cliente,
            producto=self.producto,
            fecha_venta=date.today(),
            valor=1200000,
            numero_factura='FAC-001',
        )

    def test_garantia_fecha_fin_debe_ser_posterior(self):
        garantia = Garantia(
            venta=self.venta,
            fecha_inicio=date.today(),
            fecha_fin=date.today() - timedelta(days=1),
            estado='vigente',
        )
        with self.assertRaises(ValidationError):
            garantia.full_clean()

    def test_catalogo_inicial_de_estados_existe(self):
        self.assertTrue(EstadoCaso.objects.filter(codigo='recibido').exists())
        self.assertTrue(EstadoCaso.objects.filter(es_final=True).exists())


class GarantiasViewTests(TestCase):
    def test_paginas_principales_responden(self):
        names = [
            'dashboard',
            'cliente_list',
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
        for name in names:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

# Create your tests here.
