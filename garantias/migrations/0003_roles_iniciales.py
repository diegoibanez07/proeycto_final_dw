from django.db import migrations


def crear_roles(apps, schema_editor):
    Grupo = apps.get_model('auth', 'Group')
    for nombre in ['Administrador', 'Recepcion', 'Tecnico', 'Consulta']:
        Grupo.objects.get_or_create(name=nombre)


def borrar_roles(apps, schema_editor):
    Grupo = apps.get_model('auth', 'Group')
    Grupo.objects.filter(name__in=['Administrador', 'Recepcion', 'Tecnico', 'Consulta']).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('garantias', '0002_catalogos_iniciales'),
    ]

    operations = [
        migrations.RunPython(crear_roles, borrar_roles),
    ]
