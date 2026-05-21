from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import (
    FormularioCasoReparacion,
    FormularioCategoriaProducto,
    FormularioCliente,
    FormularioDiagnostico,
    FormularioEntrega,
    FormularioEstadoCaso,
    FormularioEvidencia,
    FormularioGarantia,
    FormularioHistorialEstado,
    FormularioProducto,
    FormularioVenta,
)
from .models import (
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


class VistaPanelControl(TemplateView):
    template_name = 'garantias/dashboard.html'

    def get_context_data(self, **argumentos):
        contexto = super().get_context_data(**argumentos)
        contexto['seccion'] = 'panel'
        contexto['total_clientes'] = Cliente.objects.count()
        contexto['total_productos'] = Producto.objects.count()
        contexto['garantias_vigentes'] = Garantia.objects.filter(
            estado='vigente',
            fecha_fin__gte=timezone.localdate(),
        ).count()
        contexto['casos_abiertos'] = CasoReparacion.objects.filter(
            Q(fecha_cierre__isnull=True) | Q(estado_actual__es_final=False)
        ).distinct().count()
        contexto['casos_recientes'] = CasoReparacion.objects.select_related(
            'garantia__venta__cliente',
            'garantia__venta__producto',
            'estado_actual',
        )[:6]
        contexto['estados'] = EstadoCaso.objects.annotate(total=Count('casos_actuales')).order_by('orden')
        return contexto


class VistaBaseLista(ListView):
    template_name = 'garantias/lista.html'
    paginate_by = 10
    campos_busqueda = []
    titulo = ''
    subtitulo = ''
    nombre_url_creacion = ''
    seccion = ''

    def get_queryset(self):
        consulta_modelo = super().get_queryset()
        texto_busqueda = self.request.GET.get('q', '').strip()
        if texto_busqueda and self.campos_busqueda:
            condiciones_busqueda = Q()
            for campo_busqueda in self.campos_busqueda:
                condiciones_busqueda |= Q(**{f'{campo_busqueda}__icontains': texto_busqueda})
            consulta_modelo = consulta_modelo.filter(condiciones_busqueda)
        return consulta_modelo

    def get_context_data(self, **argumentos):
        contexto = super().get_context_data(**argumentos)
        contexto.update(
            titulo=self.titulo,
            subtitulo=self.subtitulo,
            nombre_url_creacion=self.nombre_url_creacion,
            seccion=self.seccion,
            texto_busqueda=self.request.GET.get('q', '').strip(),
            registros=contexto['object_list'],
        )
        return contexto


class VistaBaseDetalle(DetailView):
    template_name = 'garantias/detalle.html'
    titulo = ''
    nombre_url_lista = ''
    nombre_url_edicion = ''
    nombre_url_eliminacion = ''
    seccion = ''
    campos_detalle = []

    def get_context_data(self, **argumentos):
        contexto = super().get_context_data(**argumentos)
        contexto.update(
            titulo=self.titulo,
            nombre_url_lista=self.nombre_url_lista,
            nombre_url_edicion=self.nombre_url_edicion,
            nombre_url_eliminacion=self.nombre_url_eliminacion,
            seccion=self.seccion,
            registro=self.object,
            detalles=[(etiqueta, self.obtener_valor(ruta)) for etiqueta, ruta in self.campos_detalle],
        )
        return contexto

    def obtener_valor(self, ruta):
        valor = self.object
        for parte_ruta in ruta.split('.'):
            valor = getattr(valor, parte_ruta)
            if callable(valor):
                valor = valor()
        return valor


class VistaBaseFormulario:
    template_name = 'garantias/formulario.html'
    titulo = ''
    nombre_url_lista = ''
    seccion = ''

    def get_context_data(self, **argumentos):
        contexto = super().get_context_data(**argumentos)
        contexto.update(
            titulo=self.titulo,
            nombre_url_lista=self.nombre_url_lista,
            seccion=self.seccion,
            formulario=contexto.get('form'),
        )
        return contexto

    def form_valid(self, formulario):
        messages.success(self.request, 'Registro guardado correctamente.')
        return super().form_valid(formulario)


class VistaBaseEliminacion(DeleteView):
    template_name = 'garantias/confirmar_eliminacion.html'
    titulo = ''
    nombre_url_lista = ''
    seccion = ''

    def get_context_data(self, **argumentos):
        contexto = super().get_context_data(**argumentos)
        contexto.update(
            titulo=self.titulo,
            nombre_url_lista=self.nombre_url_lista,
            seccion=self.seccion,
            registro=self.object,
        )
        return contexto

    def form_valid(self, formulario):
        messages.success(self.request, 'Registro eliminado correctamente.')
        return super().form_valid(formulario)


class VistaListaCliente(VistaBaseLista):
    model = Cliente
    titulo = 'Clientes'
    subtitulo = 'Personas y empresas con equipos vendidos o en reparacion.'
    nombre_url_creacion = 'cliente_create'
    seccion = 'clientes'
    campos_busqueda = ['nombre', 'documento', 'telefono', 'correo']


class VistaDetalleCliente(VistaBaseDetalle):
    model = Cliente
    titulo = 'Detalle del cliente'
    nombre_url_lista = 'cliente_list'
    nombre_url_edicion = 'cliente_update'
    nombre_url_eliminacion = 'cliente_delete'
    seccion = 'clientes'
    campos_detalle = [
        ('Documento', 'documento'),
        ('Telefono', 'telefono'),
        ('Correo', 'correo'),
        ('Direccion', 'direccion'),
        ('Ciudad', 'ciudad'),
        ('Activo', 'activo'),
    ]


class VistaCreacionCliente(VistaBaseFormulario, CreateView):
    model = Cliente
    form_class = FormularioCliente
    titulo = 'Nuevo cliente'
    nombre_url_lista = 'cliente_list'
    seccion = 'clientes'


class VistaEdicionCliente(VistaBaseFormulario, UpdateView):
    model = Cliente
    form_class = FormularioCliente
    titulo = 'Editar cliente'
    nombre_url_lista = 'cliente_list'
    seccion = 'clientes'


class VistaEliminacionCliente(VistaBaseEliminacion):
    model = Cliente
    success_url = reverse_lazy('cliente_list')
    titulo = 'Eliminar cliente'
    nombre_url_lista = 'cliente_list'
    seccion = 'clientes'


class VistaListaCategoria(VistaBaseLista):
    model = CategoriaProducto
    titulo = 'Categorias'
    subtitulo = 'Clasificacion normalizada para los productos.'
    nombre_url_creacion = 'categoria_create'
    seccion = 'productos'
    campos_busqueda = ['nombre', 'descripcion']


class VistaDetalleCategoria(VistaBaseDetalle):
    model = CategoriaProducto
    titulo = 'Detalle de categoria'
    nombre_url_lista = 'categoria_list'
    nombre_url_edicion = 'categoria_update'
    nombre_url_eliminacion = 'categoria_delete'
    seccion = 'productos'
    campos_detalle = [('Nombre', 'nombre'), ('Descripcion', 'descripcion'), ('Activo', 'activo')]


class VistaCreacionCategoria(VistaBaseFormulario, CreateView):
    model = CategoriaProducto
    form_class = FormularioCategoriaProducto
    titulo = 'Nueva categoria'
    nombre_url_lista = 'categoria_list'
    seccion = 'productos'


class VistaEdicionCategoria(VistaBaseFormulario, UpdateView):
    model = CategoriaProducto
    form_class = FormularioCategoriaProducto
    titulo = 'Editar categoria'
    nombre_url_lista = 'categoria_list'
    seccion = 'productos'


class VistaEliminacionCategoria(VistaBaseEliminacion):
    model = CategoriaProducto
    success_url = reverse_lazy('categoria_list')
    titulo = 'Eliminar categoria'
    nombre_url_lista = 'categoria_list'
    seccion = 'productos'


class VistaListaProducto(VistaBaseLista):
    model = Producto
    titulo = 'Productos'
    subtitulo = 'Inventario serializado para ventas, garantias y reparaciones.'
    nombre_url_creacion = 'producto_create'
    seccion = 'productos'
    campos_busqueda = ['nombre', 'marca', 'modelo', 'serial', 'categoria__nombre']

    def get_queryset(self):
        return super().get_queryset().select_related('categoria')


class VistaDetalleProducto(VistaBaseDetalle):
    model = Producto
    titulo = 'Detalle del producto'
    nombre_url_lista = 'producto_list'
    nombre_url_edicion = 'producto_update'
    nombre_url_eliminacion = 'producto_delete'
    seccion = 'productos'
    campos_detalle = [
        ('Nombre', 'nombre'),
        ('Marca', 'marca'),
        ('Modelo', 'modelo'),
        ('Serial', 'serial'),
        ('Categoria', 'categoria'),
        ('Descripcion', 'descripcion'),
    ]


class VistaCreacionProducto(VistaBaseFormulario, CreateView):
    model = Producto
    form_class = FormularioProducto
    titulo = 'Nuevo producto'
    nombre_url_lista = 'producto_list'
    seccion = 'productos'


class VistaEdicionProducto(VistaBaseFormulario, UpdateView):
    model = Producto
    form_class = FormularioProducto
    titulo = 'Editar producto'
    nombre_url_lista = 'producto_list'
    seccion = 'productos'


class VistaEliminacionProducto(VistaBaseEliminacion):
    model = Producto
    success_url = reverse_lazy('producto_list')
    titulo = 'Eliminar producto'
    nombre_url_lista = 'producto_list'
    seccion = 'productos'


class VistaListaVenta(VistaBaseLista):
    model = Venta
    titulo = 'Ventas'
    subtitulo = 'Registro comercial que activa la trazabilidad de garantia.'
    nombre_url_creacion = 'venta_create'
    seccion = 'ventas'
    campos_busqueda = ['numero_factura', 'cliente__nombre', 'producto__serial']

    def get_queryset(self):
        return super().get_queryset().select_related('cliente', 'producto')


class VistaDetalleVenta(VistaBaseDetalle):
    model = Venta
    titulo = 'Detalle de venta'
    nombre_url_lista = 'venta_list'
    nombre_url_edicion = 'venta_update'
    nombre_url_eliminacion = 'venta_delete'
    seccion = 'ventas'
    campos_detalle = [
        ('Cliente', 'cliente'),
        ('Producto', 'producto'),
        ('Fecha', 'fecha_venta'),
        ('Valor', 'valor'),
        ('Factura', 'numero_factura'),
        ('Observaciones', 'observaciones'),
    ]


class VistaCreacionVenta(VistaBaseFormulario, CreateView):
    model = Venta
    form_class = FormularioVenta
    titulo = 'Nueva venta'
    nombre_url_lista = 'venta_list'
    seccion = 'ventas'


class VistaEdicionVenta(VistaBaseFormulario, UpdateView):
    model = Venta
    form_class = FormularioVenta
    titulo = 'Editar venta'
    nombre_url_lista = 'venta_list'
    seccion = 'ventas'


class VistaEliminacionVenta(VistaBaseEliminacion):
    model = Venta
    success_url = reverse_lazy('venta_list')
    titulo = 'Eliminar venta'
    nombre_url_lista = 'venta_list'
    seccion = 'ventas'


class VistaListaGarantia(VistaBaseLista):
    model = Garantia
    titulo = 'Garantias'
    subtitulo = 'Cobertura, vigencia y condiciones asociadas a cada venta.'
    nombre_url_creacion = 'garantia_create'
    seccion = 'garantias'
    campos_busqueda = ['venta__numero_factura', 'venta__cliente__nombre', 'venta__producto__serial', 'estado']

    def get_queryset(self):
        return super().get_queryset().select_related('venta__cliente', 'venta__producto')


class VistaDetalleGarantia(VistaBaseDetalle):
    model = Garantia
    titulo = 'Detalle de garantia'
    nombre_url_lista = 'garantia_list'
    nombre_url_edicion = 'garantia_update'
    nombre_url_eliminacion = 'garantia_delete'
    seccion = 'garantias'
    campos_detalle = [
        ('Venta', 'venta'),
        ('Inicio', 'fecha_inicio'),
        ('Fin', 'fecha_fin'),
        ('Estado', 'get_estado_display'),
        ('Vigente hoy', 'esta_vigente'),
        ('Condiciones', 'condiciones'),
    ]


class VistaCreacionGarantia(VistaBaseFormulario, CreateView):
    model = Garantia
    form_class = FormularioGarantia
    titulo = 'Nueva garantia'
    nombre_url_lista = 'garantia_list'
    seccion = 'garantias'


class VistaEdicionGarantia(VistaBaseFormulario, UpdateView):
    model = Garantia
    form_class = FormularioGarantia
    titulo = 'Editar garantia'
    nombre_url_lista = 'garantia_list'
    seccion = 'garantias'


class VistaEliminacionGarantia(VistaBaseEliminacion):
    model = Garantia
    success_url = reverse_lazy('garantia_list')
    titulo = 'Eliminar garantia'
    nombre_url_lista = 'garantia_list'
    seccion = 'garantias'


class VistaListaCaso(VistaBaseLista):
    model = CasoReparacion
    titulo = 'Casos tecnicos'
    subtitulo = 'Flujo completo de ingreso, revision, reparacion y cierre.'
    nombre_url_creacion = 'caso_create'
    seccion = 'casos'
    campos_busqueda = [
        'descripcion_falla',
        'tecnico_responsable',
        'garantia__venta__cliente__nombre',
        'garantia__venta__producto__serial',
        'estado_actual__nombre',
    ]

    def get_queryset(self):
        return super().get_queryset().select_related(
            'garantia__venta__cliente',
            'garantia__venta__producto',
            'estado_actual',
        )


class VistaDetalleCaso(VistaBaseDetalle):
    model = CasoReparacion
    titulo = 'Detalle del caso'
    nombre_url_lista = 'caso_list'
    nombre_url_edicion = 'caso_update'
    nombre_url_eliminacion = 'caso_delete'
    seccion = 'casos'
    campos_detalle = [
        ('Cliente', 'cliente'),
        ('Producto', 'producto'),
        ('Garantia', 'garantia'),
        ('Prioridad', 'get_prioridad_display'),
        ('Estado actual', 'estado_actual'),
        ('Ingreso', 'fecha_ingreso'),
        ('Cierre', 'fecha_cierre'),
        ('Tecnico', 'tecnico_responsable'),
        ('Falla', 'descripcion_falla'),
    ]

    def get_queryset(self):
        return super().get_queryset().select_related(
            'garantia__venta__cliente',
            'garantia__venta__producto',
            'estado_actual',
        ).prefetch_related('diagnosticos', 'evidencias', 'historial_estados')

    def get_context_data(self, **argumentos):
        contexto = super().get_context_data(**argumentos)
        contexto['diagnosticos'] = self.object.diagnosticos.all()[:5]
        contexto['evidencias'] = self.object.evidencias.all()[:6]
        contexto['historial'] = self.object.historial_estados.select_related('estado')[:8]
        return contexto


class VistaCreacionCaso(VistaBaseFormulario, CreateView):
    model = CasoReparacion
    form_class = FormularioCasoReparacion
    titulo = 'Nuevo caso tecnico'
    nombre_url_lista = 'caso_list'
    seccion = 'casos'

    def form_valid(self, formulario):
        respuesta = super().form_valid(formulario)
        HistorialEstado.objects.create(
            caso=self.object,
            estado=self.object.estado_actual,
            comentario='Apertura del caso tecnico.',
        )
        return respuesta


class VistaEdicionCaso(VistaBaseFormulario, UpdateView):
    model = CasoReparacion
    form_class = FormularioCasoReparacion
    titulo = 'Editar caso tecnico'
    nombre_url_lista = 'caso_list'
    seccion = 'casos'

    def form_valid(self, formulario):
        identificador_estado_anterior = CasoReparacion.objects.get(pk=self.object.pk).estado_actual_id
        if formulario.instance.estado_actual.es_final and not formulario.instance.fecha_cierre:
            formulario.instance.fecha_cierre = timezone.now()
        respuesta = super().form_valid(formulario)
        if identificador_estado_anterior != self.object.estado_actual_id:
            HistorialEstado.objects.create(
                caso=self.object,
                estado=self.object.estado_actual,
                comentario='Cambio de estado desde la edicion del caso.',
            )
        return respuesta


class VistaEliminacionCaso(VistaBaseEliminacion):
    model = CasoReparacion
    success_url = reverse_lazy('caso_list')
    titulo = 'Eliminar caso tecnico'
    nombre_url_lista = 'caso_list'
    seccion = 'casos'


class VistaListaDiagnostico(VistaBaseLista):
    model = Diagnostico
    titulo = 'Diagnosticos'
    subtitulo = 'Analisis tecnicos y soluciones propuestas.'
    nombre_url_creacion = 'diagnostico_create'
    seccion = 'diagnosticos'
    campos_busqueda = ['tecnico', 'diagnostico', 'solucion', 'caso__garantia__venta__cliente__nombre']

    def get_queryset(self):
        return super().get_queryset().select_related('caso__garantia__venta__cliente')


class VistaDetalleDiagnostico(VistaBaseDetalle):
    model = Diagnostico
    titulo = 'Detalle de diagnostico'
    nombre_url_lista = 'diagnostico_list'
    nombre_url_edicion = 'diagnostico_update'
    nombre_url_eliminacion = 'diagnostico_delete'
    seccion = 'diagnosticos'
    campos_detalle = [
        ('Caso', 'caso'),
        ('Tecnico', 'tecnico'),
        ('Diagnostico', 'diagnostico'),
        ('Solucion', 'solucion'),
        ('Requiere repuesto', 'requiere_repuesto'),
        ('Costo estimado', 'costo_estimado'),
        ('Fecha', 'fecha'),
    ]


class VistaCreacionDiagnostico(VistaBaseFormulario, CreateView):
    model = Diagnostico
    form_class = FormularioDiagnostico
    titulo = 'Nuevo diagnostico'
    nombre_url_lista = 'diagnostico_list'
    seccion = 'diagnosticos'


class VistaEdicionDiagnostico(VistaBaseFormulario, UpdateView):
    model = Diagnostico
    form_class = FormularioDiagnostico
    titulo = 'Editar diagnostico'
    nombre_url_lista = 'diagnostico_list'
    seccion = 'diagnosticos'


class VistaEliminacionDiagnostico(VistaBaseEliminacion):
    model = Diagnostico
    success_url = reverse_lazy('diagnostico_list')
    titulo = 'Eliminar diagnostico'
    nombre_url_lista = 'diagnostico_list'
    seccion = 'diagnosticos'


class VistaListaEvidencia(VistaBaseLista):
    model = Evidencia
    titulo = 'Fotos y evidencias'
    subtitulo = 'Archivos de ingreso, reparacion, diagnostico y entrega.'
    nombre_url_creacion = 'evidencia_create'
    seccion = 'evidencias'
    campos_busqueda = ['descripcion', 'tipo', 'caso__garantia__venta__cliente__nombre']

    def get_queryset(self):
        return super().get_queryset().select_related('caso__garantia__venta__cliente')


class VistaDetalleEvidencia(VistaBaseDetalle):
    model = Evidencia
    titulo = 'Detalle de evidencia'
    nombre_url_lista = 'evidencia_list'
    nombre_url_edicion = 'evidencia_update'
    nombre_url_eliminacion = 'evidencia_delete'
    seccion = 'evidencias'
    campos_detalle = [
        ('Caso', 'caso'),
        ('Tipo', 'get_tipo_display'),
        ('Descripcion', 'descripcion'),
        ('Fecha', 'fecha'),
    ]


class VistaCreacionEvidencia(VistaBaseFormulario, CreateView):
    model = Evidencia
    form_class = FormularioEvidencia
    titulo = 'Nueva evidencia'
    nombre_url_lista = 'evidencia_list'
    seccion = 'evidencias'


class VistaEdicionEvidencia(VistaBaseFormulario, UpdateView):
    model = Evidencia
    form_class = FormularioEvidencia
    titulo = 'Editar evidencia'
    nombre_url_lista = 'evidencia_list'
    seccion = 'evidencias'


class VistaEliminacionEvidencia(VistaBaseEliminacion):
    model = Evidencia
    success_url = reverse_lazy('evidencia_list')
    titulo = 'Eliminar evidencia'
    nombre_url_lista = 'evidencia_list'
    seccion = 'evidencias'


class VistaListaEstado(VistaBaseLista):
    model = EstadoCaso
    titulo = 'Estados'
    subtitulo = 'Catalogo del flujo tecnico y de entrega.'
    nombre_url_creacion = 'estado_create'
    seccion = 'estados'
    campos_busqueda = ['codigo', 'nombre', 'descripcion']


class VistaDetalleEstado(VistaBaseDetalle):
    model = EstadoCaso
    titulo = 'Detalle de estado'
    nombre_url_lista = 'estado_list'
    nombre_url_edicion = 'estado_update'
    nombre_url_eliminacion = 'estado_delete'
    seccion = 'estados'
    campos_detalle = [
        ('Codigo', 'codigo'),
        ('Nombre', 'nombre'),
        ('Orden', 'orden'),
        ('Final', 'es_final'),
        ('Activo', 'activo'),
        ('Descripcion', 'descripcion'),
    ]


class VistaCreacionEstado(VistaBaseFormulario, CreateView):
    model = EstadoCaso
    form_class = FormularioEstadoCaso
    titulo = 'Nuevo estado'
    nombre_url_lista = 'estado_list'
    seccion = 'estados'


class VistaEdicionEstado(VistaBaseFormulario, UpdateView):
    model = EstadoCaso
    form_class = FormularioEstadoCaso
    titulo = 'Editar estado'
    nombre_url_lista = 'estado_list'
    seccion = 'estados'


class VistaEliminacionEstado(VistaBaseEliminacion):
    model = EstadoCaso
    success_url = reverse_lazy('estado_list')
    titulo = 'Eliminar estado'
    nombre_url_lista = 'estado_list'
    seccion = 'estados'


class VistaListaHistorial(VistaBaseLista):
    model = HistorialEstado
    titulo = 'Historial de estados'
    subtitulo = 'Auditoria cronologica de cada movimiento del caso.'
    nombre_url_creacion = 'historial_create'
    seccion = 'estados'
    campos_busqueda = ['comentario', 'estado__nombre', 'caso__garantia__venta__cliente__nombre']

    def get_queryset(self):
        return super().get_queryset().select_related('caso', 'estado')


class VistaDetalleHistorial(VistaBaseDetalle):
    model = HistorialEstado
    titulo = 'Detalle de historial'
    nombre_url_lista = 'historial_list'
    nombre_url_edicion = 'historial_update'
    nombre_url_eliminacion = 'historial_delete'
    seccion = 'estados'
    campos_detalle = [('Caso', 'caso'), ('Estado', 'estado'), ('Fecha', 'fecha'), ('Comentario', 'comentario')]


class VistaCreacionHistorial(VistaBaseFormulario, CreateView):
    model = HistorialEstado
    form_class = FormularioHistorialEstado
    titulo = 'Nuevo movimiento'
    nombre_url_lista = 'historial_list'
    seccion = 'estados'

    def form_valid(self, formulario):
        respuesta = super().form_valid(formulario)
        formulario.instance.caso.estado_actual = formulario.instance.estado
        if formulario.instance.estado.es_final and not formulario.instance.caso.fecha_cierre:
            formulario.instance.caso.fecha_cierre = formulario.instance.fecha
        formulario.instance.caso.save(update_fields=['estado_actual', 'fecha_cierre', 'actualizado'])
        return respuesta


class VistaEdicionHistorial(VistaBaseFormulario, UpdateView):
    model = HistorialEstado
    form_class = FormularioHistorialEstado
    titulo = 'Editar movimiento'
    nombre_url_lista = 'historial_list'
    seccion = 'estados'


class VistaEliminacionHistorial(VistaBaseEliminacion):
    model = HistorialEstado
    success_url = reverse_lazy('historial_list')
    titulo = 'Eliminar movimiento'
    nombre_url_lista = 'historial_list'
    seccion = 'estados'


class VistaListaEntrega(VistaBaseLista):
    model = Entrega
    titulo = 'Entregas'
    subtitulo = 'Cierre documentado del producto reparado o devuelto.'
    nombre_url_creacion = 'entrega_create'
    seccion = 'entregas'
    campos_busqueda = ['entregado_a', 'documento_entrega', 'caso__garantia__venta__cliente__nombre']

    def get_queryset(self):
        return super().get_queryset().select_related('caso__garantia__venta__cliente')


class VistaDetalleEntrega(VistaBaseDetalle):
    model = Entrega
    titulo = 'Detalle de entrega'
    nombre_url_lista = 'entrega_list'
    nombre_url_edicion = 'entrega_update'
    nombre_url_eliminacion = 'entrega_delete'
    seccion = 'entregas'
    campos_detalle = [
        ('Caso', 'caso'),
        ('Fecha', 'fecha_entrega'),
        ('Entregado a', 'entregado_a'),
        ('Documento', 'documento_entrega'),
        ('Recibido conforme', 'recibido_conforme'),
        ('Observaciones', 'observaciones'),
    ]


class VistaCreacionEntrega(VistaBaseFormulario, CreateView):
    model = Entrega
    form_class = FormularioEntrega
    titulo = 'Nueva entrega'
    nombre_url_lista = 'entrega_list'
    seccion = 'entregas'

    def form_valid(self, formulario):
        respuesta = super().form_valid(formulario)
        estado_final = EstadoCaso.objects.filter(es_final=True, activo=True).order_by('orden').last()
        if estado_final:
            caso = self.object.caso
            caso.estado_actual = estado_final
            caso.fecha_cierre = self.object.fecha_entrega
            caso.save(update_fields=['estado_actual', 'fecha_cierre', 'actualizado'])
            HistorialEstado.objects.create(
                caso=caso,
                estado=estado_final,
                fecha=self.object.fecha_entrega,
                comentario='Caso cerrado por entrega del producto.',
            )
        return respuesta


class VistaEdicionEntrega(VistaBaseFormulario, UpdateView):
    model = Entrega
    form_class = FormularioEntrega
    titulo = 'Editar entrega'
    nombre_url_lista = 'entrega_list'
    seccion = 'entregas'


class VistaEliminacionEntrega(VistaBaseEliminacion):
    model = Entrega
    success_url = reverse_lazy('entrega_list')
    titulo = 'Eliminar entrega'
    nombre_url_lista = 'entrega_list'
    seccion = 'entregas'


def avanzar_estado_caso(request, caso_id):
    caso = get_object_or_404(CasoReparacion, pk=caso_id)
    siguiente_estado = EstadoCaso.objects.filter(
        activo=True,
        orden__gt=caso.estado_actual.orden,
    ).order_by('orden').first()
    if siguiente_estado:
        caso.estado_actual = siguiente_estado
        if siguiente_estado.es_final and not caso.fecha_cierre:
            caso.fecha_cierre = timezone.now()
        caso.save(update_fields=['estado_actual', 'fecha_cierre', 'actualizado'])
        HistorialEstado.objects.create(
            caso=caso,
            estado=siguiente_estado,
            comentario='Avance rapido de estado.',
        )
        messages.success(request, f'Caso movido a {siguiente_estado.nombre}.')
    return redirect(caso)

