# Plataforma de garantias y reparaciones

Sistema Django para negocios que necesitan controlar productos vendidos,
garantias, diagnosticos tecnicos, evidencias, estados y entrega final.

## Modulos

- Clientes
- Productos y categorias
- Ventas
- Garantias
- Casos tecnicos
- Diagnosticos
- Fotos y evidencias
- Estados e historial
- Entrega y cierre

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
