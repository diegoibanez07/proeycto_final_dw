from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import CategoriaProducto, Cliente, EstadoCaso, Garantia, Producto, Venta


class PruebasModelosGarantias(TestCase):
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


class PruebasVistasGarantias(TestCase):
    def setUp(self):
        self.administrador = User.objects.create_superuser(
            username='admin',
            password='clave-segura',
            email='admin@example.com',
        )
        self.recepcionista = User.objects.create_user(username='recepcion', password='clave-segura')
        self.recepcionista.groups.add(Group.objects.get(name='Recepcion'))
        self.tecnico = User.objects.create_user(username='tecnico', password='clave-segura')
        self.tecnico.groups.add(Group.objects.get(name='Tecnico'))

    def test_usuario_sin_ingresar_es_redirigido_al_login(self):
        respuesta = self.client.get(reverse('dashboard'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse('login'), respuesta.url)

    def test_paginas_principales_responden_para_administrador(self):
        self.client.force_login(self.administrador)
        nombres = [
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
        for nombre in nombres:
            with self.subTest(nombre=nombre):
                respuesta = self.client.get(reverse(nombre))
                self.assertEqual(respuesta.status_code, 200)

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
