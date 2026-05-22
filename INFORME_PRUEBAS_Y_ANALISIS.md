# Informe de pruebas y analisis de calidad

## 1. Objetivo

Este documento resume las pruebas realizadas sobre la plataforma de garantias y
reparaciones para validar que:

- Los modelos respetan reglas de negocio.
- Los formularios rechazan datos incorrectos.
- Las vistas responden correctamente.
- Los roles bloquean accesos indebidos.
- El flujo principal funciona sin errores absurdos.
- El comando de carga masiva crea datos relacionados.

## 2. Comandos ejecutados

Validacion general de Django:

```powershell
python manage.py check
```

Resultado:

```text
System check identified no issues (0 silenced).
```

Validacion de migraciones:

```powershell
python manage.py makemigrations --check --dry-run
```

Resultado:

```text
No changes detected
```

Pruebas automatizadas:

```powershell
python manage.py test
```

Resultado:

```text
Found 30 test(s).
Ran 30 tests
OK
```

## 3. Pruebas de modelos

Se probaron reglas de negocio directamente en los modelos.

### Catalogos iniciales

Se valida que existan:

- Estados iniciales del flujo.
- Estado final.
- Grupos de roles: Administrador, Recepcion, Tecnico y Consulta.

### Garantias

Se valida:

- La fecha final debe ser posterior a la fecha inicial.
- La garantia no puede iniciar antes de la venta.

Riesgo cubierto:

- Evita garantias con fechas imposibles.
- Evita garantias creadas antes de que exista la venta.

### Casos tecnicos

Se valida:

- La fecha de cierre no puede ser anterior al ingreso.
- No se puede abrir caso sobre una garantia anulada.

Riesgo cubierto:

- Evita casos cerrados antes de existir.
- Evita usar garantias anuladas para procesos tecnicos.

### Evidencias

Se valida:

- Solo se aceptan archivos JPG, JPEG, PNG, WEBP o PDF.

Riesgo cubierto:

- Evita subir archivos peligrosos o no relacionados como `.exe`.

### Entregas

Se valida:

- La entrega no puede ocurrir antes del ingreso del caso.

Riesgo cubierto:

- Evita cerrar casos con fechas incoherentes.

## 4. Pruebas de formularios

Se probaron formularios con datos incorrectos.

### Formulario de cliente

Caso probado:

- Telefono invalido.

Resultado esperado:

- El formulario no es valido.
- El error queda asociado al campo `telefono`.

### Formulario de venta

Caso probado:

- Valor negativo.

Resultado esperado:

- El formulario no es valido.
- El error queda asociado al campo `valor`.

### Formulario de garantia

Caso probado:

- Fecha final menor que fecha inicial.

Resultado esperado:

- El formulario no es valido.
- El error queda asociado al campo `fecha_fin`.

### Formulario de diagnostico

Caso probado:

- Costo estimado negativo.

Resultado esperado:

- El formulario no es valido.
- El error queda asociado al campo `costo_estimado`.

### Formulario de evidencia

Caso probado:

- Archivo `.exe`.

Resultado esperado:

- El formulario no es valido.
- El error queda asociado al campo `imagen`.

### Formulario de entrega

Caso probado:

- Fecha de entrega anterior al ingreso del caso.

Resultado esperado:

- El formulario no es valido.
- El error queda asociado al campo `fecha_entrega`.

## 5. Pruebas de roles y permisos

Se probaron usuarios con diferentes roles.

### Usuario anonimo

Caso probado:

- Entrar al panel sin iniciar sesion.

Resultado esperado:

- Redireccion al login.

### Modulo publico

Casos probados:

- Inicio publico abre sin login.
- Servicios publicos abre sin login.
- Consulta publica encuentra caso por factura.
- Consulta publica encuentra caso por numero de caso.
- Consulta publica no muestra informacion si el documento no coincide.

Resultado esperado:

- Las paginas publicas responden 200 sin autenticacion.
- La consulta solo devuelve estado cuando documento y codigo coinciden.

### Usuario sin rol

Caso probado:

- Usuario autenticado sin grupo intenta entrar al panel.

Resultado esperado:

- Respuesta 403.

### Administrador

Caso probado:

- Acceso a todas las listas principales.

Resultado esperado:

- Todas responden 200.

Listas cubiertas:

- Panel.
- Clientes.
- Categorias.
- Productos.
- Ventas.
- Garantias.
- Casos.
- Diagnosticos.
- Evidencias.
- Estados.
- Historial.
- Entregas.

### Recepcion

Casos probados:

- Puede entrar a ventas.
- No puede entrar a estados.
- Puede abrir formularios de clientes, productos, ventas, garantias, casos,
  evidencias y entregas.

Resultado esperado:

- Modulos permitidos responden 200.
- Estados responde 403.

### Tecnico

Casos probados:

- Puede entrar a diagnosticos.
- No puede entrar a ventas.
- Puede abrir diagnosticos e historial.
- Puede avanzar estado de un caso.

Resultado esperado:

- Diagnosticos responde 200.
- Ventas responde 403.
- Al avanzar estado, el estado cambia y se crea historial.

### Consulta

Casos probados:

- Puede ver casos.
- Puede ver diagnosticos.
- No puede crear casos.

Resultado esperado:

- Listas de lectura responden 200.
- Formularios de creacion responden 403.

## 6. Pruebas de vistas

Se probaron detalles de todos los modulos principales con administrador:

- Cliente.
- Categoria.
- Producto.
- Venta.
- Garantia.
- Caso.
- Diagnostico.
- Evidencia.
- Estado.
- Historial.
- Entrega.

Resultado esperado:

- Todas las pantallas de detalle responden 200.

Tambien se probo busqueda en clientes:

- Buscar `Laura`.
- El resultado contiene `Laura Martinez`.

## 7. Prueba de creacion real desde vista

Se probo crear un cliente desde la vista usando el rol Recepcion.

Resultado esperado:

- La respuesta redirige correctamente.
- El cliente queda creado en base de datos.

Esto valida que el flujo de formulario, permisos, guardado y redireccion funciona.

## 8. Prueba de carga masiva

Se probo el comando:

```powershell
python manage.py cargar_datos_reales --cantidad 12 --limpiar
```

Resultado esperado:

- 12 clientes.
- 12 productos.
- 12 ventas.
- 12 garantias.
- 12 casos.
- 12 diagnosticos.
- 12 evidencias.
- 12 historiales.
- 12 entregas.

La prueba confirma que el comando respeta relaciones y no crea registros
desconectados.

## 9. Validacion local con usuarios de prueba

Se validaron los usuarios creados en la base local:

```text
digoe -> login correcto, estados 200
admin_garantias -> login correcto, estados 200
recepcion_garantias -> login correcto, ventas 200, estados 403
tecnico_garantias -> login correcto, diagnosticos 200, ventas 403
consulta_garantias -> login correcto, casos 200, crear caso 403
```

## 10. Conclusiones

La aplicacion queda validada en estos puntos:

- Login obligatorio.
- Roles aplicados.
- Bloqueo 403 para accesos indebidos.
- Modelos con validaciones de negocio.
- Formularios rechazando datos incoherentes.
- Vistas principales funcionando.
- Detalles de todos los modulos funcionando.
- Accion de avance de estado controlada por rol tecnico.
- Busqueda funcionando.
- Carga masiva funcionando con relaciones.

## 11. Riesgos restantes y mejoras recomendadas

Aunque las pruebas actuales cubren el flujo principal, se recomiendan mejoras
futuras:

- Agregar pruebas con navegador real usando Playwright para validar diseño y
  experiencia visual.
- Agregar portal publico de consulta para clientes finales si el negocio lo
  necesita.
- Agregar exportacion PDF de entrega o acta de servicio.
- Agregar auditoria de usuario que hizo cada cambio.
- Agregar asignacion formal de tecnico al caso usando usuario del sistema en vez
  de texto libre.
- Agregar pruebas de rendimiento si se esperan cientos de miles de registros.
