from django.db import migrations


def crear_catalogos(apps, schema_editor):
    EstadoCaso = apps.get_model('garantias', 'EstadoCaso')
    CategoriaProducto = apps.get_model('garantias', 'CategoriaProducto')

    estados = [
        ('recibido', 'Recibido', '#2563eb', 1, False),
        ('en-diagnostico', 'En diagnostico', '#7c3aed', 2, False),
        ('diagnosticado', 'Diagnosticado', '#d97706', 3, False),
        ('en-reparacion', 'En reparacion', '#0f766e', 4, False),
        ('listo-para-entrega', 'Listo para entrega', '#16a34a', 5, False),
        ('entregado', 'Entregado', '#475569', 6, True),
        ('cerrado', 'Cerrado', '#111827', 7, True),
    ]
    for codigo, nombre, color, orden, es_final in estados:
        EstadoCaso.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'color': color,
                'orden': orden,
                'es_final': es_final,
                'activo': True,
            },
        )

    categorias = ['Celulares', 'Electrodomesticos', 'Computadores', 'Muebles', 'Accesorios']
    for nombre in categorias:
        CategoriaProducto.objects.get_or_create(nombre=nombre, defaults={'activo': True})


def borrar_catalogos(apps, schema_editor):
    EstadoCaso = apps.get_model('garantias', 'EstadoCaso')
    CategoriaProducto = apps.get_model('garantias', 'CategoriaProducto')
    EstadoCaso.objects.filter(codigo__in=[
        'recibido',
        'en-diagnostico',
        'diagnosticado',
        'en-reparacion',
        'listo-para-entrega',
        'entregado',
        'cerrado',
    ]).delete()
    CategoriaProducto.objects.filter(nombre__in=[
        'Celulares',
        'Electrodomesticos',
        'Computadores',
        'Muebles',
        'Accesorios',
    ]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('garantias', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_catalogos, borrar_catalogos),
    ]
