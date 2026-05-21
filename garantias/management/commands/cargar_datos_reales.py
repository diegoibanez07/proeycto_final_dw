import base64
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from random import Random

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from garantias.models import (
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


class Command(BaseCommand):
    help = 'Carga datos masivos realistas para visualizar la plataforma con volumen.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=1000,
            help='Cantidad de registros operativos por tabla principal.',
        )
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Elimina datos operativos existentes antes de cargar.',
        )

    @transaction.atomic
    def handle(self, *argumentos, **opciones):
        cantidad = opciones['cantidad']
        generador = Random(20260521)

        if opciones['limpiar']:
            self.stdout.write('Limpiando datos operativos anteriores...')
            Entrega.objects.all().delete()
            HistorialEstado.objects.all().delete()
            Evidencia.objects.all().delete()
            Diagnostico.objects.all().delete()
            CasoReparacion.objects.all().delete()
            Garantia.objects.all().delete()
            Venta.objects.all().delete()
            Producto.objects.all().delete()
            Cliente.objects.all().delete()

        categorias = self.obtener_categorias()
        estados = self.obtener_estados()
        estado_recibido = estados['recibido']
        estado_diagnostico = estados['en-diagnostico']
        estado_diagnosticado = estados['diagnosticado']
        estado_reparacion = estados['en-reparacion']
        estado_listo = estados['listo-para-entrega']
        estado_entregado = estados['entregado']
        estado_cerrado = estados['cerrado']

        clientes = self.crear_clientes(cantidad, generador)
        productos = self.crear_productos(cantidad, generador, categorias)
        ventas = self.crear_ventas(cantidad, generador, clientes, productos)
        garantias = self.crear_garantias(cantidad, generador, ventas)
        casos = self.crear_casos(
            cantidad,
            generador,
            garantias,
            [estado_recibido, estado_diagnostico, estado_diagnosticado, estado_reparacion, estado_listo, estado_entregado],
        )
        self.crear_diagnosticos(cantidad, generador, casos)
        self.crear_evidencias(cantidad, generador, casos)
        self.crear_historial(cantidad, generador, casos, [estado_recibido, estado_diagnostico, estado_diagnosticado, estado_reparacion, estado_listo, estado_entregado, estado_cerrado])
        self.crear_entregas(cantidad, generador, casos, estado_entregado)

        self.stdout.write(self.style.SUCCESS('Carga terminada correctamente.'))
        self.stdout.write(f'Clientes: {Cliente.objects.count()}')
        self.stdout.write(f'Productos: {Producto.objects.count()}')
        self.stdout.write(f'Ventas: {Venta.objects.count()}')
        self.stdout.write(f'Garantias: {Garantia.objects.count()}')
        self.stdout.write(f'Casos: {CasoReparacion.objects.count()}')
        self.stdout.write(f'Diagnosticos: {Diagnostico.objects.count()}')
        self.stdout.write(f'Evidencias: {Evidencia.objects.count()}')
        self.stdout.write(f'Historial estados: {HistorialEstado.objects.count()}')
        self.stdout.write(f'Entregas: {Entrega.objects.count()}')

    def obtener_categorias(self):
        datos = [
            ('Celulares', 'Equipos moviles vendidos en tienda.'),
            ('Computadores portatiles', 'Portatiles de uso personal y corporativo.'),
            ('Computadores de escritorio', 'Equipos de escritorio y estaciones de trabajo.'),
            ('Electrodomesticos', 'Productos electricos para hogar y oficina.'),
            ('Monitores', 'Pantallas, monitores y televisores.'),
            ('Impresoras', 'Impresoras, multifuncionales y escaneres.'),
            ('Tabletas', 'Tabletas para estudio y trabajo.'),
            ('Accesorios', 'Cargadores, cables, teclados y perifericos.'),
        ]
        categorias = []
        for nombre, descripcion in datos:
            categoria, _ = CategoriaProducto.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': descripcion, 'activo': True},
            )
            categorias.append(categoria)
        return categorias

    def obtener_estados(self):
        datos = [
            ('recibido', 'Recibido', '#2563eb', 1, False),
            ('en-diagnostico', 'En diagnostico', '#7c3aed', 2, False),
            ('diagnosticado', 'Diagnosticado', '#d97706', 3, False),
            ('en-reparacion', 'En reparacion', '#0f766e', 4, False),
            ('listo-para-entrega', 'Listo para entrega', '#16a34a', 5, False),
            ('entregado', 'Entregado', '#475569', 6, True),
            ('cerrado', 'Cerrado', '#111827', 7, True),
        ]
        estados = {}
        for codigo, nombre, color, orden, es_final in datos:
            estado, _ = EstadoCaso.objects.update_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'color': color,
                    'orden': orden,
                    'es_final': es_final,
                    'activo': True,
                },
            )
            estados[codigo] = estado
        return estados

    def crear_clientes(self, cantidad, generador):
        nombres = ['Andres', 'Camila', 'Santiago', 'Valentina', 'Juan', 'Laura', 'Mateo', 'Daniela', 'Sebastian', 'Natalia', 'Carlos', 'Paula', 'Felipe', 'Manuela', 'Diego', 'Carolina', 'Alejandro', 'Mariana', 'Julian', 'Sofia']
        apellidos = ['Gomez', 'Rodriguez', 'Martinez', 'Garcia', 'Lopez', 'Hernandez', 'Perez', 'Sanchez', 'Ramirez', 'Torres', 'Diaz', 'Vargas', 'Castro', 'Rojas', 'Moreno', 'Jimenez', 'Ortiz', 'Gutierrez', 'Ruiz', 'Mendoza']
        ciudades = ['Bogota', 'Medellin', 'Cali', 'Barranquilla', 'Bucaramanga', 'Pereira', 'Manizales', 'Cartagena', 'Ibague', 'Villavicencio']
        clientes = []
        for numero in range(1, cantidad + 1):
            nombre = f'{generador.choice(nombres)} {generador.choice(apellidos)} {generador.choice(apellidos)}'
            ciudad = generador.choice(ciudades)
            clientes.append(Cliente(
                tipo_documento='CC',
                documento=f'{1000000000 + numero}',
                nombre=nombre,
                telefono=f'3{generador.randint(0, 9)}{generador.randint(10000000, 99999999)}',
                correo=f'{nombre.lower().replace(" ", ".")}.{numero}@correo.com',
                direccion=f'Calle {generador.randint(1, 170)} #{generador.randint(1, 90)}-{generador.randint(1, 99)}',
                ciudad=ciudad,
                activo=True,
            ))
        return Cliente.objects.bulk_create(clientes, batch_size=500)

    def crear_productos(self, cantidad, generador, categorias):
        referencias = {
            'Celulares': [('Celular', 'Samsung', 'Galaxy A54'), ('Celular', 'Motorola', 'Edge 40'), ('Celular', 'Xiaomi', 'Redmi Note 13'), ('Celular', 'Apple', 'iPhone 13')],
            'Computadores portatiles': [('Portatil', 'Lenovo', 'ThinkPad E14'), ('Portatil', 'HP', 'Pavilion 15'), ('Portatil', 'Dell', 'Inspiron 3520'), ('Portatil', 'Asus', 'Vivobook 16')],
            'Computadores de escritorio': [('Equipo de escritorio', 'HP', 'ProDesk 400'), ('Equipo de escritorio', 'Dell', 'OptiPlex 7010'), ('Equipo de escritorio', 'Lenovo', 'ThinkCentre M70')],
            'Electrodomesticos': [('Lavadora', 'LG', 'Carga Frontal 19Kg'), ('Nevera', 'Samsung', 'No Frost 300L'), ('Microondas', 'Haceb', 'HM-1.1')],
            'Monitores': [('Monitor', 'LG', 'UltraGear 24'), ('Monitor', 'Samsung', 'Curvo 27'), ('Televisor', 'Sony', 'Bravia 43')],
            'Impresoras': [('Impresora', 'Epson', 'EcoTank L3250'), ('Impresora', 'HP', 'Smart Tank 580'), ('Multifuncional', 'Brother', 'DCP-T720')],
            'Tabletas': [('Tableta', 'Samsung', 'Galaxy Tab A9'), ('Tableta', 'Lenovo', 'Tab M10'), ('Tableta', 'Apple', 'iPad 10')],
            'Accesorios': [('Cargador', 'Belkin', 'USB-C 65W'), ('Teclado', 'Logitech', 'K380'), ('Mouse', 'Microsoft', 'Bluetooth 3600')],
        }
        productos = []
        for numero in range(1, cantidad + 1):
            categoria = categorias[(numero - 1) % len(categorias)]
            nombre, marca, modelo = generador.choice(referencias[categoria.nombre])
            productos.append(Producto(
                nombre=nombre,
                marca=marca,
                modelo=modelo,
                serial=f'{marca[:3].upper()}-{modelo.replace(" ", "").replace("-", "")[:8].upper()}-{numero:06d}',
                categoria=categoria,
                descripcion=f'{nombre} {marca} {modelo} vendido con revision visual inicial y accesorios declarados.',
                activo=True,
            ))
        return Producto.objects.bulk_create(productos, batch_size=500)

    def crear_ventas(self, cantidad, generador, clientes, productos):
        ventas = []
        hoy = timezone.localdate()
        for indice in range(cantidad):
            fecha_venta = hoy - timedelta(days=generador.randint(15, 900))
            ventas.append(Venta(
                cliente=clientes[indice],
                producto=productos[indice],
                fecha_venta=fecha_venta,
                valor=Decimal(generador.randint(180000, 5800000)),
                numero_factura=f'FAC-{fecha_venta:%Y%m}-{indice + 1:06d}',
                observaciones='Venta registrada con factura y soporte de garantia comercial.',
            ))
        return Venta.objects.bulk_create(ventas, batch_size=500)

    def crear_garantias(self, cantidad, generador, ventas):
        garantias = []
        hoy = timezone.localdate()
        for venta in ventas:
            meses = generador.choice([6, 12, 18, 24])
            fecha_fin = venta.fecha_venta + timedelta(days=meses * 30)
            if fecha_fin < hoy:
                estado = 'vencida'
            else:
                estado = 'vigente'
            if generador.randint(1, 100) <= 3:
                estado = 'anulada'
            garantias.append(Garantia(
                venta=venta,
                fecha_inicio=venta.fecha_venta,
                fecha_fin=fecha_fin,
                estado=estado,
                condiciones='Cubre defectos de fabricacion. No cubre golpes, humedad, manipulacion externa ni desgaste normal.',
            ))
        return Garantia.objects.bulk_create(garantias, batch_size=500)

    def crear_casos(self, cantidad, generador, garantias, estados):
        fallas = [
            'El equipo no enciende despues de varias horas de carga.',
            'Presenta reinicios inesperados durante el uso normal.',
            'La pantalla muestra lineas y parpadeos intermitentes.',
            'El puerto de carga no reconoce el adaptador original.',
            'El sistema se bloquea al abrir aplicaciones de trabajo.',
            'El ventilador genera ruido superior al normal.',
            'La bateria se descarga rapidamente.',
            'El teclado presenta teclas sin respuesta.',
            'No conecta a redes inalambricas conocidas.',
            'El producto presenta calentamiento excesivo.',
        ]
        tecnicos = ['Carlos Mesa', 'Diana Pardo', 'Miguel Cardenas', 'Luisa Bernal', 'Oscar Salazar', 'Tatiana Leon']
        casos = []
        ahora = timezone.now()
        garantias_validas = [garantia for garantia in garantias if garantia.estado != 'anulada']
        for indice in range(cantidad):
            garantia = garantias_validas[indice % len(garantias_validas)]
            fecha_ingreso = ahora - timedelta(days=generador.randint(1, 220), hours=generador.randint(0, 7))
            estado = estados[indice % len(estados)]
            fecha_cierre = fecha_ingreso + timedelta(days=generador.randint(2, 20)) if estado.es_final else None
            casos.append(CasoReparacion(
                garantia=garantia,
                descripcion_falla=generador.choice(fallas),
                estado_actual=estado,
                prioridad=generador.choice(['baja', 'media', 'alta', 'critica']),
                fecha_ingreso=fecha_ingreso,
                fecha_cierre=fecha_cierre,
                tecnico_responsable=generador.choice(tecnicos),
                observaciones='Caso recibido con revision inicial, accesorios declarados y evidencia fotografica.',
            ))
        return CasoReparacion.objects.bulk_create(casos, batch_size=500)

    def crear_diagnosticos(self, cantidad, generador, casos):
        hallazgos = [
            ('Se identifica falla en circuito de carga.', 'Reemplazar conector y realizar limpieza de placa.'),
            ('Se detecta bateria con ciclos elevados.', 'Cambiar bateria y calibrar sistema.'),
            ('Memoria con errores de lectura.', 'Reemplazar modulo de memoria y ejecutar prueba extendida.'),
            ('Sistema operativo con archivos corruptos.', 'Reinstalar sistema y respaldar informacion disponible.'),
            ('Pantalla con flex sulfatado.', 'Cambiar flex y validar imagen continua.'),
            ('Ventilacion obstruida por polvo interno.', 'Realizar mantenimiento preventivo y cambio de pasta termica.'),
            ('Cargador entrega voltaje inestable.', 'Reemplazar adaptador por unidad certificada.'),
        ]
        diagnosticos = []
        for indice in range(cantidad):
            caso = casos[indice % len(casos)]
            diagnostico, solucion = generador.choice(hallazgos)
            diagnosticos.append(Diagnostico(
                caso=caso,
                tecnico=caso.tecnico_responsable,
                diagnostico=diagnostico,
                solucion=solucion,
                requiere_repuesto=generador.choice([True, False, True]),
                costo_estimado=Decimal(generador.randint(0, 450000)),
                fecha=caso.fecha_ingreso + timedelta(hours=generador.randint(2, 36)),
            ))
        return Diagnostico.objects.bulk_create(diagnosticos, batch_size=500)

    def crear_evidencias(self, cantidad, generador, casos):
        carpeta = Path('evidencias/carga_masiva')
        tipos = ['ingreso', 'diagnostico', 'reparacion', 'entrega']
        evidencias = []
        for indice in range(cantidad):
            caso = casos[indice % len(casos)]
            tipo = tipos[indice % len(tipos)]
            ruta_relativa = carpeta / f'evidencia_caso_{caso.id:05d}_{tipo}.png'
            self.crear_archivo_evidencia(ruta_relativa)
            evidencias.append(Evidencia(
                caso=caso,
                tipo=tipo,
                imagen=str(ruta_relativa),
                descripcion=f'Evidencia de {tipo} para validar condiciones del producto y avance del servicio.',
                fecha=caso.fecha_ingreso + timedelta(hours=generador.randint(1, 80)),
            ))
        return Evidencia.objects.bulk_create(evidencias, batch_size=500)

    def crear_archivo_evidencia(self, ruta_relativa):
        ruta_absoluta = Path(settings.MEDIA_ROOT) / ruta_relativa
        if ruta_absoluta.exists():
            return
        ruta_absoluta.parent.mkdir(parents=True, exist_ok=True)
        imagen_base64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII='
        ruta_absoluta.write_bytes(base64.b64decode(imagen_base64))

    def crear_historial(self, cantidad, generador, casos, estados):
        historiales = []
        for indice in range(cantidad):
            caso = casos[indice % len(casos)]
            estado = estados[min(indice % len(estados), len(estados) - 1)]
            historiales.append(HistorialEstado(
                caso=caso,
                estado=estado,
                fecha=caso.fecha_ingreso + timedelta(hours=generador.randint(1, 120)),
                comentario=f'Caso actualizado a {estado.nombre.lower()} segun revision del area responsable.',
            ))
        return HistorialEstado.objects.bulk_create(historiales, batch_size=500)

    def crear_entregas(self, cantidad, generador, casos, estado_entregado):
        entregas = []
        for indice in range(cantidad):
            caso = casos[indice % len(casos)]
            fecha_entrega = caso.fecha_ingreso + timedelta(days=generador.randint(3, 25), hours=generador.randint(1, 6))
            entregas.append(Entrega(
                caso=caso,
                fecha_entrega=fecha_entrega,
                entregado_a=caso.cliente.nombre,
                documento_entrega=caso.cliente.documento,
                recibido_conforme=generador.choice([True, True, True, False]),
                observaciones='Producto entregado con revision frente al cliente y cierre documentado del servicio.',
            ))
            caso.estado_actual = estado_entregado
            caso.fecha_cierre = fecha_entrega
        Entrega.objects.bulk_create(entregas, batch_size=500)
        CasoReparacion.objects.bulk_update(casos, ['estado_actual', 'fecha_cierre'], batch_size=500)
        return entregas
