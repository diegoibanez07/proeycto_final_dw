# Documentacion completa: Plataforma de garantias y reparaciones

## 1. Que es el sistema

La plataforma sirve para controlar todo el proceso de garantia y reparacion de
un producto vendido por la empresa.

El objetivo es que el negocio no pierda informacion sobre:

- Quien compro el producto.
- Que producto compro.
- En que venta o factura quedo registrado.
- Si el producto tiene garantia.
- Que falla reporto el cliente.
- Que diagnostico hizo el tecnico.
- Que fotos o documentos sirven como evidencia.
- En que estado va el caso.
- Cuando se entrega el producto y a quien.

En palabras simples: el sistema acompana el producto desde la venta hasta el
cierre de la garantia o reparacion.

## 2. Usuarios y roles

El sistema no es publico. Para entrar, cada persona debe iniciar sesion.

La entrada esta en:

```text
/cuenta/login/
```

Despues de iniciar sesion, el menu cambia segun el rol del usuario. Si alguien
intenta abrir una pagina que no le corresponde escribiendo la URL manualmente,
el sistema muestra una pagina `403 Acceso no autorizado`.

### Administrador

Es el usuario con control total.

Puede:

- Ver todos los modulos.
- Crear, editar y eliminar registros.
- Configurar estados.
- Revisar historial.
- Administrar usuarios desde el admin de Django.
- Asignar roles a los usuarios.

Este rol normalmente lo usa el dueno, gerente o encargado del sistema.

### Recepcion

Es el personal que atiende al cliente y registra informacion comercial.

Puede:

- Registrar clientes.
- Registrar productos.
- Registrar ventas.
- Crear garantias.
- Abrir casos tecnicos.
- Subir evidencias.
- Registrar entregas.

No deberia configurar estados internos ni eliminar informacion critica.

### Tecnico

Es el personal que revisa y repara los productos.

Puede:

- Ver casos tecnicos.
- Registrar diagnosticos.
- Subir evidencias tecnicas.
- Actualizar historial de estados.
- Avanzar el estado de un caso.

No ve ventas ni garantias como modulo comercial principal, porque su trabajo
esta centrado en el proceso tecnico.

### Consulta

Es un usuario de solo lectura.

Puede:

- Ver informacion permitida.
- Consultar clientes, productos, ventas, garantias, casos, diagnosticos,
  evidencias y entregas segun el menu habilitado.

No puede crear, editar, eliminar ni avanzar estados.

## 3. Tabla resumida de permisos

| Modulo | Administrador | Recepcion | Tecnico | Consulta |
| --- | --- | --- | --- | --- |
| Panel | Si | Si | Si | Si |
| Clientes | Si | Si | No | Si |
| Productos | Si | Si | No | Si |
| Ventas | Si | Si | No | Si |
| Garantias | Si | Si | No | Si |
| Casos tecnicos | Si | Si | Si | Si |
| Diagnosticos | Si | No | Si | Si |
| Evidencias | Si | Si | Si | Si |
| Estados | Si | No | No | No |
| Historial | Si | No | Si | Si |
| Entregas | Si | Si | No | Si |

## 4. Modulos principales

### Clientes

Aqui se registra la persona o empresa que compra el producto.

Datos principales:

- Tipo de documento.
- Documento.
- Nombre.
- Telefono.
- Correo.
- Direccion.
- Ciudad.
- Estado activo o inactivo.

El cliente puede tener muchas ventas.

### Categorias de productos

Sirven para organizar los productos.

Ejemplos:

- Celulares.
- Electrodomesticos.
- Computadores.
- Muebles.
- Accesorios.

Un producto pertenece a una categoria.

### Productos

Aqui se registra el producto vendido o atendido.

Datos principales:

- Nombre.
- Marca.
- Modelo.
- Serial.
- Categoria.
- Descripcion.
- Estado activo o inactivo.

El serial es unico, porque ayuda a identificar exactamente el producto fisico.

### Ventas

La venta une un cliente con un producto.

Datos principales:

- Cliente.
- Producto.
- Fecha de venta.
- Valor.
- Numero de factura.
- Observaciones.

Una venta puede tener una garantia.

### Garantias

La garantia depende de una venta. Esto evita crear garantias sin saber que
producto se vendio, a quien y en que factura.

Datos principales:

- Venta.
- Fecha de inicio.
- Fecha de fin.
- Estado: vigente, vencida o anulada.
- Condiciones.

Validaciones:

- La fecha final debe ser posterior a la fecha inicial.
- La garantia no puede iniciar antes de la venta.

### Casos tecnicos

El caso tecnico es el centro del proceso de reparacion.

Se crea cuando un cliente trae un producto por garantia o revision.

Datos principales:

- Garantia relacionada.
- Descripcion de la falla.
- Estado actual.
- Prioridad.
- Fecha de ingreso.
- Fecha de cierre.
- Tecnico responsable.
- Observaciones.

Un caso tecnico puede tener muchos diagnosticos, muchas evidencias y muchos
movimientos de historial.

### Diagnosticos

Los diagnosticos registran lo que encontro el tecnico.

Datos principales:

- Caso.
- Tecnico.
- Diagnostico.
- Solucion propuesta o aplicada.
- Si requiere repuesto.
- Costo estimado.
- Fecha.

Un caso puede tener varios diagnosticos, por ejemplo uno inicial y otro despues
de probar la reparacion.

### Evidencias

Las evidencias son fotos o archivos que prueban el estado del producto.

Datos principales:

- Caso.
- Tipo de evidencia: ingreso, diagnostico, reparacion o entrega.
- Archivo.
- Descripcion.
- Fecha.

Formatos permitidos:

- JPG.
- JPEG.
- PNG.
- WEBP.
- PDF.

Ejemplos de uso:

- Foto del producto cuando entra.
- Foto del golpe o dano.
- Foto interna tomada por el tecnico.
- PDF con soporte o documento externo.
- Foto del producto al momento de entrega.

### Estados

Los estados representan el avance del caso.

Estados iniciales creados por migracion:

- Recibido.
- En diagnostico.
- Diagnosticado.
- En reparacion.
- Listo para entrega.
- Entregado.
- Cerrado.

Cada estado tiene:

- Codigo.
- Nombre.
- Descripcion.
- Color.
- Orden.
- Si es final o no.
- Si esta activo o no.

Solo el administrador debe modificar esta tabla.

### Historial de estados

El historial guarda la trazabilidad del caso.

Cada vez que un caso cambia de estado, se puede registrar:

- Caso.
- Estado.
- Fecha.
- Comentario.

Esto permite saber que paso, cuando paso y en que punto del flujo estaba el
producto.

### Entrega

La entrega representa el cierre documentado del proceso.

Datos principales:

- Caso.
- Fecha de entrega.
- Persona que recibe.
- Documento de quien recibe.
- Si recibe conforme.
- Observaciones.

Cuando se registra una entrega, el sistema intenta cerrar el caso moviendolo a
un estado final.

## 5. Flujo completo del sistema

Este es el flujo normal de trabajo.

### Paso 1. Registrar cliente

Recepcion registra al cliente con su documento, telefono y datos de contacto.

Ejemplo:

```text
Cliente: Maria Gomez
Documento: 123456789
Telefono: 3001234567
Correo: maria@example.com
```

### Paso 2. Registrar producto

Recepcion registra el producto con su marca, modelo y serial.

Ejemplo:

```text
Producto: Celular
Marca: Samsung
Modelo: A54
Serial: SAM-A54-001
Categoria: Celulares
```

### Paso 3. Registrar venta

Recepcion crea una venta que conecta el cliente con el producto.

Ejemplo:

```text
Cliente: Maria Gomez
Producto: Samsung A54
Factura: FAC-1001
Fecha venta: 2026-05-21
Valor: 1200000
```

Desde este punto ya se sabe quien compro, que compro y bajo que factura.

### Paso 4. Crear garantia

Recepcion crea la garantia asociada a la venta.

Ejemplo:

```text
Venta: FAC-1001
Fecha inicio: 2026-05-21
Fecha fin: 2027-05-21
Estado: Vigente
```

La garantia queda conectada directamente con la venta, el cliente y el
producto.

### Paso 5. Abrir caso tecnico

Cuando el cliente vuelve con una falla, recepcion o tecnico abre un caso.

Ejemplo:

```text
Garantia: FAC-1001
Falla: El celular no carga
Prioridad: Alta
Estado actual: Recibido
Tecnico responsable: Carlos
```

Al crear el caso, el sistema tambien genera un primer movimiento en el historial
indicando la apertura del caso.

### Paso 6. Subir evidencia de ingreso

Recepcion o tecnico sube fotos del estado inicial del producto.

Ejemplos:

- Foto frontal del equipo.
- Foto del puerto de carga.
- Foto de rayones o golpes.

Esto protege al negocio y al cliente porque deja evidencia del estado en que
entro el producto.

### Paso 7. Registrar diagnostico

El tecnico revisa el producto y registra el diagnostico.

Ejemplo:

```text
Tecnico: Carlos
Diagnostico: Puerto de carga sulfatado
Solucion: Limpieza y cambio del conector
Requiere repuesto: Si
Costo estimado: 80000
```

### Paso 8. Actualizar estado

El tecnico puede mover el caso entre estados.

Ejemplo de avance:

```text
Recibido -> En diagnostico -> Diagnosticado -> En reparacion
```

Cada cambio puede quedar en el historial con fecha y comentario.

### Paso 9. Subir evidencia de reparacion

Durante o despues de la reparacion, el tecnico puede subir nuevas evidencias.

Ejemplos:

- Foto del repuesto instalado.
- Foto del equipo funcionando.
- Documento PDF de prueba.

### Paso 10. Marcar listo para entrega

Cuando el producto ya esta reparado o revisado, se cambia el estado a:

```text
Listo para entrega
```

Esto le indica a recepcion que puede llamar al cliente o preparar la entrega.

### Paso 11. Registrar entrega

Recepcion registra quien recibe el producto.

Ejemplo:

```text
Entregado a: Maria Gomez
Documento: 123456789
Recibido conforme: Si
Observaciones: Cliente revisa funcionamiento en mostrador.
```

Al registrar la entrega, el sistema cierra el proceso moviendo el caso a un
estado final si existe uno configurado.

### Paso 12. Caso cerrado

El caso queda cerrado con:

- Cliente.
- Producto.
- Venta.
- Garantia.
- Falla.
- Diagnosticos.
- Evidencias.
- Historial de estados.
- Entrega.

Esto crea trazabilidad completa.

## 6. Como se ve para cada tipo de usuario

### Si entra un administrador

Vera el menu completo:

- Panel.
- Clientes.
- Productos.
- Ventas.
- Garantias.
- Casos tecnicos.
- Diagnosticos.
- Fotos.
- Estados.
- Entrega.

Puede crear, editar y eliminar.

### Si entra recepcion

Vera modulos enfocados en atencion al cliente:

- Panel.
- Clientes.
- Productos.
- Ventas.
- Garantias.
- Casos tecnicos.
- Fotos.
- Entrega.

No vera configuracion de estados ni diagnosticos como modulo principal.

### Si entra tecnico

Vera modulos enfocados en reparacion:

- Panel.
- Casos tecnicos.
- Diagnosticos.
- Fotos.
- Historial.

No vera ventas, garantias o clientes como area comercial.

### Si entra consulta

Vera informacion de lectura.

No vera botones de crear, editar, eliminar ni avanzar estados.

## 7. Que pasa si alguien intenta entrar donde no debe

Hay dos controles:

1. El menu no muestra modulos no permitidos.
2. La vista bloquea el acceso aunque la persona escriba la URL manualmente.

Ejemplo:

```text
Un tecnico intenta abrir /ventas/
Resultado: 403 Acceso no autorizado
```

Ejemplo:

```text
Recepcion intenta abrir /estados/
Resultado: 403 Acceso no autorizado
```

## 8. Relaciones principales de la base de datos

La base esta normalizada para evitar duplicacion innecesaria.

Relaciones:

- Un cliente tiene muchas ventas.
- Un producto puede estar en ventas.
- Una venta pertenece a un cliente.
- Una venta pertenece a un producto.
- Una garantia pertenece a una venta.
- Una garantia puede tener varios casos de reparacion.
- Un caso pertenece a una garantia.
- Un caso tiene muchos diagnosticos.
- Un caso tiene muchas evidencias.
- Un caso tiene muchos movimientos de historial.
- Un caso puede tener una entrega.
- Un estado puede aparecer en muchos casos y muchos historiales.

Flujo relacional resumido:

```text
Cliente -> Venta -> Garantia -> Caso tecnico -> Diagnosticos
                                      |
                                      -> Evidencias
                                      |
                                      -> Historial de estados
                                      |
                                      -> Entrega
```

## 9. Validaciones importantes

El sistema valida:

- Documento de cliente unico.
- Serial de producto unico.
- Numero de factura unico.
- Valor de venta mayor o igual a cero.
- Fecha final de garantia posterior a la fecha inicial.
- Garantia no puede iniciar antes de la venta.
- No se puede abrir caso sobre garantia anulada.
- Fecha de cierre no puede ser anterior a fecha de ingreso.
- Evidencias solo permiten JPG, JPEG, PNG, WEBP o PDF.
- Entrega no puede ser anterior al ingreso del caso.

## 10. Pantallas principales

### Panel

Muestra resumen general:

- Total de clientes.
- Total de productos.
- Garantias vigentes.
- Casos abiertos.
- Casos recientes.
- Estados del sistema.

### Listas

Cada modulo tiene una lista con:

- Buscador.
- Tarjetas de registros.
- Accion de ver detalle.
- Boton de crear solo si el rol lo permite.

### Formularios

Los formularios permiten crear o editar registros.

El sistema muestra errores si algun dato no cumple las reglas.

### Detalle

La pantalla de detalle muestra la informacion completa de un registro.

En los casos tecnicos, ademas muestra:

- Diagnosticos recientes.
- Evidencias.
- Historial de estados.
- Accion de avanzar estado si el rol lo permite.

### Login

Pantalla donde el usuario ingresa con su usuario y contrasena.

## 11. Como crear usuarios y asignar roles

1. Crear un superusuario:

```powershell
python manage.py createsuperuser
```

2. Entrar al admin:

```text
http://127.0.0.1:8000/admin/
```

3. Crear o abrir un usuario.

4. En la seccion de grupos, asignar uno:

- Administrador.
- Recepcion.
- Tecnico.
- Consulta.

5. Guardar.

6. El usuario ya puede iniciar sesion en:

```text
http://127.0.0.1:8000/cuenta/login/
```

## 12. Ejemplo completo de un caso real

Supongamos que una tienda vende un computador.

1. Recepcion crea el cliente `Juan Perez`.
2. Recepcion crea el producto `Portatil Lenovo`, serial `LEN-001`.
3. Recepcion crea la venta `FAC-2001`.
4. Recepcion crea la garantia de 12 meses.
5. Despues de tres meses, Juan vuelve porque el computador no prende.
6. Recepcion abre un caso tecnico con estado `Recibido`.
7. Recepcion sube fotos del equipo al ingreso.
8. El tecnico revisa el equipo.
9. El tecnico registra diagnostico: `falla en cargador`.
10. El tecnico cambia estado a `Diagnosticado`.
11. El tecnico cambia estado a `En reparacion`.
12. El tecnico sube evidencia del equipo encendido.
13. El tecnico cambia estado a `Listo para entrega`.
14. Recepcion entrega el equipo a Juan.
15. Recepcion registra la entrega y el documento.
16. El caso queda cerrado.

Al final, la empresa puede consultar todo el historial del caso.

## 13. Instalacion y ejecucion local

Crear entorno:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Instalar librerias:

```powershell
pip install -r requirements.txt
```

Aplicar migraciones:

```powershell
python manage.py migrate
```

Crear superusuario:

```powershell
python manage.py createsuperuser
```

Ejecutar:

```powershell
python manage.py runserver
```

Abrir:

```text
http://127.0.0.1:8000/
```

## 14. Cargar datos realistas

El proyecto incluye un comando para llenar la base con informacion realista y
relacionada.

Ejecutar:

```powershell
python manage.py cargar_datos_reales --cantidad 1000 --limpiar
```

Que hace:

- Limpia los datos operativos anteriores si se usa `--limpiar`.
- Crea clientes con nombres, documentos, telefonos, correos y direcciones.
- Crea productos con marcas, modelos, seriales y categorias.
- Crea ventas relacionadas con clientes y productos.
- Crea garantias relacionadas con ventas.
- Crea casos tecnicos relacionados con garantias.
- Crea diagnosticos relacionados con casos.
- Crea evidencias relacionadas con casos y archivos en `media/`.
- Crea historial de estados relacionado con casos.
- Crea entregas relacionadas con casos.

Los catalogos como categorias y estados no se inflan a 1000 porque son tablas de
configuracion. Mantener pocos estados permite que el flujo siga siendo real y
entendible.

Resultado esperado con `--cantidad 1000`:

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

## 15. PostgreSQL

El proyecto puede usar PostgreSQL si existen estas variables en `.env`:

```env
POSTGRES_DB=garantias_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Si esas variables no existen, Django usa SQLite para desarrollo local.

## 16. Resumen final

La plataforma funciona como un flujo operativo:

```text
Cliente -> Producto -> Venta -> Garantia -> Caso tecnico -> Diagnostico
                                                    -> Evidencias
                                                    -> Historial
                                                    -> Entrega
                                                    -> Cierre
```

Cada usuario ve solo lo que necesita para su trabajo. Recepcion atiende al
cliente, tecnico resuelve el caso, consulta revisa informacion y administrador
controla todo.
