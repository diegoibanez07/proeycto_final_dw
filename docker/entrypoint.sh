#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
    python manage.py createsuperuser --noinput || true
fi

if [ "$CARGAR_DATOS_INICIALES" = "1" ]; then
    python manage.py shell -c "import os; from django.core.management import call_command; from garantias.models import Cliente; cantidad=int(os.environ.get('CANTIDAD_DATOS_INICIALES', '100')); print('Datos iniciales ya existen; no se cargan de nuevo.') if Cliente.objects.exists() else call_command('cargar_datos_reales', cantidad=cantidad)"
fi

exec "$@"
