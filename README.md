# Plataforma de garantias y reparaciones

Sistema Django para negocios que necesitan controlar productos vendidos,
garantias, diagnosticos tecnicos, evidencias, estados y entrega final.

El proyecto conserva una estructura Django por aplicaciones, rutas y plantillas
como la base indicada en `https://github.com/ithan1985/django.git`, pero
orientada al dominio de garantias y reparaciones. No se agrego Docker/YAML en
esta fase para permitir pruebas locales con `runserver`.

La explicacion completa del flujo, roles, pantallas y funcionamiento esta en
[DOCUMENTACION.md](DOCUMENTACION.md).

El manual de uso con usuarios de prueba, roles y permisos esta en
[MANUAL_USO_ROLES.md](MANUAL_USO_ROLES.md).

El informe de pruebas, validaciones y analisis de calidad esta en
[INFORME_PRUEBAS_Y_ANALISIS.md](INFORME_PRUEBAS_Y_ANALISIS.md).

## Modulos

- Publico: inicio, servicios y consulta de estado sin login
- Clientes
- Productos y categorias
- Ventas
- Garantias
- Casos tecnicos
- Diagnosticos
- Fotos y evidencias
- Estados e historial
- Entrega y cierre

## Roles

La plataforma exige inicio de sesion. Los grupos iniciales se crean con las
migraciones:

- `Administrador`: ve y administra todo.
- `Recepcion`: clientes, productos, ventas, garantias, casos, evidencias y entregas.
- `Tecnico`: casos, diagnosticos, evidencias e historial de estados.
- `Consulta`: solo lectura de los modulos operativos permitidos.

Para asignar un rol, entra al admin de Django, abre el usuario y agregalo al
grupo correspondiente.

## Instalacion

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

La app queda disponible en `http://127.0.0.1:8000/`.

Rutas principales:

```text
/                  Modulo publico
/servicios/         Servicios ofrecidos
/consulta-estado/   Consulta publica de estado
/panel/             Panel privado con login
/cuenta/login/      Ingreso del personal
```

## Cargar datos realistas

Para poblar la base con volumen y revisar como se ve el sistema:

```powershell
python manage.py cargar_datos_reales --cantidad 1000 --limpiar
```

Esto crea 1000 registros operativos relacionados: clientes, productos, ventas,
garantias, casos, diagnosticos, evidencias, historial y entregas.

## PostgreSQL

Copia `.env.example` a `.env` y define:

```env
POSTGRES_DB=garantias_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Cuando esas variables existen, `config/settings.py` usa PostgreSQL. Si no
existen, usa SQLite para desarrollo local.
