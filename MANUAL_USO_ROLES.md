# Manual de uso, roles y usuarios de prueba

## 1. Proposito de la aplicacion

La aplicacion tiene un modulo publico y modulos privados. El modulo publico
permite mostrar los servicios y consultar el estado basico de un producto sin
login. Los modulos privados permiten controlar garantias y reparaciones desde la
empresa.
Su objetivo es que la empresa tenga trazabilidad completa desde que vende un
producto hasta que lo recibe por garantia, lo diagnostica, lo repara, adjunta
evidencias y lo entrega al cliente.

Los clientes no se registran ni entran al panel privado. Solo pueden usar las
paginas publicas de informacion y consulta.

Flujo general:

```text
Cliente -> Producto -> Venta -> Garantia -> Caso tecnico
                                      -> Diagnostico
                                      -> Evidencias
                                      -> Historial de estados
                                      -> Entrega
                                      -> Cierre
```

## 2. Entrada al sistema

Modulo publico:

```text
http://127.0.0.1:8000/
```

Panel privado:

```text
http://127.0.0.1:8000/panel/
```

El panel privado exige inicio de sesion.

URL de ingreso:

```text
http://127.0.0.1:8000/cuenta/login/
```

Si alguien intenta abrir la plataforma sin iniciar sesion, Django lo envia al
login. Si un usuario inicia sesion pero no tiene permisos para una seccion, el
sistema muestra una pantalla `403 Acceso no autorizado`.

## 3. Usuarios de prueba creados

Estos usuarios son solo para pruebas locales. Sirven para revisar como se ve la
aplicacion segun cada rol.

| Rol | Usuario | Clave | Uso recomendado |
| --- | --- | --- | --- |
| Superadmin | `digoe` | `diego.01` | Probar todo el sistema y entrar al admin de Django. |
| Administrador | `admin_garantias` | `admin.01` | Probar control total sin ser superusuario. |
| Recepcion | `recepcion_garantias` | `recepcion.01` | Probar atencion al cliente, ventas, garantias y entregas. |
| Tecnico | `tecnico_garantias` | `tecnico.01` | Probar diagnosticos, evidencias y avance de casos. |
| Consulta | `consulta_garantias` | `consulta.01` | Probar usuario de solo lectura. |

Importante: estos usuarios existen en la base local donde fueron creados. No se
suben a GitHub porque la base de datos local no se versiona.

## 3.1. Modulo publico sin login

El modulo publico es para personas externas o clientes que no deben entrar al
panel privado.

Rutas:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/servicios/
http://127.0.0.1:8000/consulta-estado/
```

Que puede hacer una persona sin login:

- Ver que ofrece la empresa.
- Entender el flujo de atencion.
- Consultar el estado basico de un caso con documento y numero de caso o
  factura.

Que no puede hacer:

- Entrar al panel privado.
- Crear casos.
- Editar informacion.
- Ver diagnosticos internos completos.
- Ver evidencias privadas.
- Eliminar datos.

## 4. Roles del sistema

### Superadmin

Es el usuario `digoe`. Tiene permisos de superusuario de Django.

Puede:

- Entrar a la plataforma.
- Entrar al admin de Django.
- Ver todos los modulos.
- Crear, editar y eliminar registros.
- Crear usuarios.
- Asignar roles.
- Corregir datos.
- Configurar estados.
- Revisar toda la trazabilidad.

Debe usarse para administracion general y configuracion.

### Administrador

Tiene control funcional completo dentro de la aplicacion.

Puede:

- Ver todos los modulos.
- Crear registros.
- Editar registros.
- Eliminar registros.
- Configurar estados.
- Consultar historiales.
- Ver ventas, garantias, diagnosticos, evidencias y entregas.

Limitacion:

- Si no es `is_staff`, no entra al admin de Django. El usuario de prueba
  `admin_garantias` si tiene `is_staff=True`.

### Recepcion

Es el rol para el personal que atiende al cliente.

Puede ver:

- Panel.
- Clientes.
- Productos.
- Ventas.
- Garantias.
- Casos tecnicos.
- Fotos y evidencias.
- Entregas.

Puede hacer:

- Registrar clientes.
- Registrar productos.
- Registrar ventas.
- Crear garantias.
- Abrir casos tecnicos.
- Subir evidencias.
- Registrar entregas.
- Editar informacion operativa de recepcion.

No puede:

- Entrar a Estados.
- Configurar el flujo tecnico.
- Entrar al modulo principal de diagnosticos.
- Eliminar informacion critica si no es administrador.

### Tecnico

Es el rol para quien revisa y repara productos.

Puede ver:

- Panel.
- Casos tecnicos.
- Diagnosticos.
- Fotos y evidencias.
- Historial de estados.

Puede hacer:

- Revisar casos.
- Registrar diagnosticos.
- Editar diagnosticos.
- Subir evidencias tecnicas.
- Cambiar o avanzar estados del caso.
- Registrar movimientos de historial.

No puede:

- Ver ventas.
- Ver garantias como modulo comercial.
- Ver clientes como modulo comercial.
- Registrar ventas.
- Registrar garantias.
- Registrar entregas.
- Configurar estados.

### Consulta

Es un rol de lectura.

Puede ver informacion permitida, pero no debe modificar nada.

Puede ver:

- Panel.
- Clientes.
- Productos.
- Ventas.
- Garantias.
- Casos tecnicos.
- Diagnosticos.
- Fotos y evidencias.
- Historial.
- Entregas.

No puede:

- Crear registros.
- Editar registros.
- Eliminar registros.
- Avanzar estados.
- Configurar estados.

## 5. Tabla clara de permisos

| Modulo | Superadmin | Administrador | Recepcion | Tecnico | Consulta |
| --- | --- | --- | --- | --- | --- |
| Panel | Si | Si | Si | Si | Si |
| Clientes | Si | Si | Si | No | Si lectura |
| Productos | Si | Si | Si | No | Si lectura |
| Ventas | Si | Si | Si | No | Si lectura |
| Garantias | Si | Si | Si | No | Si lectura |
| Casos tecnicos | Si | Si | Si | Si | Si lectura |
| Diagnosticos | Si | Si | No | Si | Si lectura |
| Evidencias | Si | Si | Si | Si | Si lectura |
| Estados | Si | Si | No | No | No |
| Historial | Si | Si | No | Si | Si lectura |
| Entregas | Si | Si | Si | No | Si lectura |

## 6. Como usar la aplicacion segun el flujo real

### Paso 1. Recepcion registra el cliente

Entrar con:

```text
recepcion_garantias / recepcion.01
```

Ir a:

```text
Clientes -> Crear registro
```

Registrar:

- Tipo de documento.
- Documento.
- Nombre.
- Telefono.
- Correo.
- Direccion.
- Ciudad.

Validaciones importantes:

- El documento no se puede repetir.
- El telefono debe tener formato valido.
- El correo debe tener formato valido.

### Paso 2. Recepcion registra el producto

Ir a:

```text
Productos -> Crear registro
```

Registrar:

- Nombre.
- Marca.
- Modelo.
- Serial.
- Categoria.
- Descripcion.

Validacion importante:

- El serial no se puede repetir.

### Paso 3. Recepcion registra la venta

Ir a:

```text
Ventas -> Crear registro
```

Registrar:

- Cliente.
- Producto.
- Fecha de venta.
- Valor.
- Numero de factura.
- Observaciones.

Validaciones importantes:

- El numero de factura no se puede repetir.
- El valor no puede ser negativo.

### Paso 4. Recepcion crea la garantia

Ir a:

```text
Garantias -> Crear registro
```

Registrar:

- Venta.
- Fecha de inicio.
- Fecha de fin.
- Estado.
- Condiciones.

Validaciones importantes:

- La garantia depende de una venta existente.
- La fecha final debe ser posterior a la fecha inicial.
- La garantia no puede iniciar antes de la venta.
- Una venta solo puede tener una garantia.

### Paso 5. Recepcion o tecnico abre el caso tecnico

Ir a:

```text
Casos tecnicos -> Crear registro
```

Registrar:

- Garantia.
- Descripcion de la falla.
- Estado actual.
- Prioridad.
- Fecha de ingreso.
- Tecnico responsable.
- Observaciones.

El sistema crea un historial inicial cuando se abre el caso.

Validaciones importantes:

- No se puede abrir un caso sobre una garantia anulada.
- Si hay fecha de cierre, no puede ser anterior a la fecha de ingreso.

### Paso 6. Recepcion o tecnico sube evidencias

Ir a:

```text
Fotos -> Crear registro
```

Registrar:

- Caso.
- Tipo de evidencia.
- Archivo.
- Descripcion.
- Fecha.

Formatos permitidos:

- JPG.
- JPEG.
- PNG.
- WEBP.
- PDF.

Ejemplos:

- Foto del producto al ingreso.
- Foto del dano reportado.
- Foto del repuesto.
- PDF con soporte tecnico.

### Paso 7. Tecnico registra diagnostico

Entrar con:

```text
tecnico_garantias / tecnico.01
```

Ir a:

```text
Diagnosticos -> Crear registro
```

Registrar:

- Caso.
- Tecnico.
- Diagnostico.
- Solucion.
- Si requiere repuesto.
- Costo estimado.
- Fecha.

Validacion importante:

- El costo estimado no puede ser negativo.

### Paso 8. Tecnico actualiza estado o historial

El tecnico puede entrar al detalle del caso y usar:

```text
Avanzar estado
```

Tambien puede registrar un movimiento manual:

```text
Historial -> Crear registro
```

Esto actualiza el estado actual del caso y deja trazabilidad.

### Paso 9. Recepcion registra entrega

Entrar con:

```text
recepcion_garantias / recepcion.01
```

Ir a:

```text
Entrega -> Crear registro
```

Registrar:

- Caso.
- Fecha de entrega.
- Entregado a.
- Documento de quien recibe.
- Recibido conforme.
- Observaciones.

Validacion importante:

- La entrega no puede ser anterior al ingreso del caso.

Al registrar entrega, el sistema cierra el caso usando un estado final si esta
configurado.

## 7. Como revisar la trazabilidad de un caso

Entrar a:

```text
Casos tecnicos
```

Abrir un caso.

En el detalle se ve:

- Informacion general.
- Cliente.
- Producto.
- Garantia.
- Prioridad.
- Estado actual.
- Fecha de ingreso.
- Fecha de cierre.
- Diagnosticos recientes.
- Evidencias.
- Historial de estados.

Esto permite responder preguntas como:

- Cuando entro el producto.
- Quien lo atendio.
- Que falla reporto el cliente.
- Que diagnostico se dio.
- Que evidencias hay.
- En que estado esta.
- Si ya fue entregado.

## 8. Que pasa si un usuario intenta hacer algo no permitido

Ejemplos:

```text
Recepcion entra a /estados/
Resultado: 403 Acceso no autorizado
```

```text
Tecnico entra a /ventas/
Resultado: 403 Acceso no autorizado
```

```text
Consulta intenta crear diagnostico
Resultado: 403 Acceso no autorizado
```

La aplicacion tiene dos barreras:

1. Oculta en el menu lo que el rol no debe ver.
2. Bloquea la vista aunque se escriba la URL manualmente.

## 9. Datos cargados para probar

La base local fue poblada con:

```text
Clientes: 1000
Productos: 1000
Ventas: 1000
Garantias: 1000
Casos: 1000
Diagnosticos: 1000
Evidencias: 1000
Historial estados: 1000
Entregas: 1000
```

Comando usado:

```powershell
python manage.py cargar_datos_reales --cantidad 1000 --limpiar
```

Los datos se generaron con nombres, marcas, modelos, seriales, facturas,
diagnosticos y observaciones realistas. No son usuarios reales de personas
existentes; son datos operativos para visualizar volumen.

## 10. Modulos y que debe revisar cada rol

### Administrador o superadmin

Debe revisar:

- Que existan estados del flujo.
- Que los usuarios tengan grupo.
- Que los casos cierren correctamente.
- Que las garantias esten bien registradas.
- Que los permisos funcionen.

### Recepcion

Debe revisar:

- Clientes.
- Productos.
- Ventas.
- Garantias.
- Apertura de casos.
- Evidencias de ingreso.
- Entregas.

### Tecnico

Debe revisar:

- Casos asignados o abiertos.
- Diagnosticos.
- Evidencias tecnicas.
- Historial de estados.
- Avance de estados.

### Consulta

Debe revisar:

- Informacion de lectura.
- Estado de casos.
- Evidencias.
- Entregas.

No debe encontrar botones para crear, editar, eliminar o avanzar estados.

## 11. Recomendaciones de uso

- No usar el superadmin para trabajo diario.
- Usar `recepcion_garantias` para simular atencion al cliente.
- Usar `tecnico_garantias` para simular reparacion.
- Usar `consulta_garantias` para comprobar que no pueda modificar.
- Mantener los estados simples y claros.
- Subir evidencias siempre que un producto cambie de fase.
- Registrar entrega solo cuando el cliente reciba el producto.

## 12. Resumen corto

La aplicacion permite que la empresa controle internamente:

```text
quien compro -> que compro -> que garantia tiene -> que falla reporto
-> que diagnostico recibio -> que evidencias existen -> en que estado esta
-> cuando se entrego -> quien recibio
```

Cada rol ve y hace solo lo necesario para su trabajo.
