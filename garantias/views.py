from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import (
    CasoReparacionForm,
    CategoriaProductoForm,
    ClienteForm,
    DiagnosticoForm,
    EntregaForm,
    EstadoCasoForm,
    EvidenciaForm,
    GarantiaForm,
    HistorialEstadoForm,
    ProductoForm,
    VentaForm,
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


class DashboardView(TemplateView):
    template_name = 'garantias/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_clientes'] = Cliente.objects.count()
        context['total_productos'] = Producto.objects.count()
        context['garantias_vigentes'] = Garantia.objects.filter(
            estado='vigente',
            fecha_fin__gte=timezone.localdate(),
        ).count()
        context['casos_abiertos'] = CasoReparacion.objects.filter(
            Q(fecha_cierre__isnull=True) | Q(estado_actual__es_final=False)
        ).distinct().count()
        context['casos_recientes'] = CasoReparacion.objects.select_related(
            'garantia__venta__cliente',
            'garantia__venta__producto',
            'estado_actual',
        )[:6]
        context['estados'] = EstadoCaso.objects.annotate(total=Count('casos_actuales')).order_by('orden')
        return context


class BaseListView(ListView):
    template_name = 'garantias/list.html'
    paginate_by = 10
    search_fields = []
    title = ''
    subtitle = ''
    create_url_name = ''
    section = ''

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q', '').strip()
        if query and self.search_fields:
            filters = Q()
            for field in self.search_fields:
                filters |= Q(**{f'{field}__icontains': query})
            queryset = queryset.filter(filters)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            title=self.title,
            subtitle=self.subtitle,
            create_url_name=self.create_url_name,
            section=self.section,
            query=self.request.GET.get('q', '').strip(),
        )
        return context


class BaseDetailView(DetailView):
    template_name = 'garantias/detail.html'
    title = ''
    list_url_name = ''
    update_url_name = ''
    delete_url_name = ''
    section = ''
    detail_fields = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            title=self.title,
            list_url_name=self.list_url_name,
            update_url_name=self.update_url_name,
            delete_url_name=self.delete_url_name,
            section=self.section,
            details=[(label, self.resolve_value(path)) for label, path in self.detail_fields],
        )
        return context

    def resolve_value(self, path):
        value = self.object
        for part in path.split('.'):
            value = getattr(value, part)
            if callable(value):
                value = value()
        return value


class BaseFormView:
    template_name = 'garantias/form.html'
    title = ''
    list_url_name = ''
    section = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(title=self.title, list_url_name=self.list_url_name, section=self.section)
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Registro guardado correctamente.')
        return super().form_valid(form)


class BaseDeleteView(DeleteView):
    template_name = 'garantias/confirm_delete.html'
    title = ''
    list_url_name = ''
    section = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(title=self.title, list_url_name=self.list_url_name, section=self.section)
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Registro eliminado correctamente.')
        return super().form_valid(form)


class ClienteListView(BaseListView):
    model = Cliente
    title = 'Clientes'
    subtitle = 'Personas y empresas con equipos vendidos o en reparacion.'
    create_url_name = 'cliente_create'
    section = 'clientes'
    search_fields = ['nombre', 'documento', 'telefono', 'correo']


class ClienteDetailView(BaseDetailView):
    model = Cliente
    title = 'Detalle del cliente'
    list_url_name = 'cliente_list'
    update_url_name = 'cliente_update'
    delete_url_name = 'cliente_delete'
    section = 'clientes'
    detail_fields = [
        ('Documento', 'documento'),
        ('Telefono', 'telefono'),
        ('Correo', 'correo'),
        ('Direccion', 'direccion'),
        ('Ciudad', 'ciudad'),
        ('Activo', 'activo'),
    ]


class ClienteCreateView(BaseFormView, CreateView):
    model = Cliente
    form_class = ClienteForm
    title = 'Nuevo cliente'
    list_url_name = 'cliente_list'
    section = 'clientes'


class ClienteUpdateView(BaseFormView, UpdateView):
    model = Cliente
    form_class = ClienteForm
    title = 'Editar cliente'
    list_url_name = 'cliente_list'
    section = 'clientes'


class ClienteDeleteView(BaseDeleteView):
    model = Cliente
    success_url = reverse_lazy('cliente_list')
    title = 'Eliminar cliente'
    list_url_name = 'cliente_list'
    section = 'clientes'


class CategoriaListView(BaseListView):
    model = CategoriaProducto
    title = 'Categorias'
    subtitle = 'Clasificacion normalizada para los productos.'
    create_url_name = 'categoria_create'
    section = 'productos'
    search_fields = ['nombre', 'descripcion']


class CategoriaDetailView(BaseDetailView):
    model = CategoriaProducto
    title = 'Detalle de categoria'
    list_url_name = 'categoria_list'
    update_url_name = 'categoria_update'
    delete_url_name = 'categoria_delete'
    section = 'productos'
    detail_fields = [('Nombre', 'nombre'), ('Descripcion', 'descripcion'), ('Activo', 'activo')]


class CategoriaCreateView(BaseFormView, CreateView):
    model = CategoriaProducto
    form_class = CategoriaProductoForm
    title = 'Nueva categoria'
    list_url_name = 'categoria_list'
    section = 'productos'


class CategoriaUpdateView(BaseFormView, UpdateView):
    model = CategoriaProducto
    form_class = CategoriaProductoForm
    title = 'Editar categoria'
    list_url_name = 'categoria_list'
    section = 'productos'


class CategoriaDeleteView(BaseDeleteView):
    model = CategoriaProducto
    success_url = reverse_lazy('categoria_list')
    title = 'Eliminar categoria'
    list_url_name = 'categoria_list'
    section = 'productos'


class ProductoListView(BaseListView):
    model = Producto
    title = 'Productos'
    subtitle = 'Inventario serializado para ventas, garantias y reparaciones.'
    create_url_name = 'producto_create'
    section = 'productos'
    search_fields = ['nombre', 'marca', 'modelo', 'serial', 'categoria__nombre']

    def get_queryset(self):
        return super().get_queryset().select_related('categoria')


class ProductoDetailView(BaseDetailView):
    model = Producto
    title = 'Detalle del producto'
    list_url_name = 'producto_list'
    update_url_name = 'producto_update'
    delete_url_name = 'producto_delete'
    section = 'productos'
    detail_fields = [
        ('Nombre', 'nombre'),
        ('Marca', 'marca'),
        ('Modelo', 'modelo'),
        ('Serial', 'serial'),
        ('Categoria', 'categoria'),
        ('Descripcion', 'descripcion'),
    ]


class ProductoCreateView(BaseFormView, CreateView):
    model = Producto
    form_class = ProductoForm
    title = 'Nuevo producto'
    list_url_name = 'producto_list'
    section = 'productos'


class ProductoUpdateView(BaseFormView, UpdateView):
    model = Producto
    form_class = ProductoForm
    title = 'Editar producto'
    list_url_name = 'producto_list'
    section = 'productos'


class ProductoDeleteView(BaseDeleteView):
    model = Producto
    success_url = reverse_lazy('producto_list')
    title = 'Eliminar producto'
    list_url_name = 'producto_list'
    section = 'productos'


class VentaListView(BaseListView):
    model = Venta
    title = 'Ventas'
    subtitle = 'Registro comercial que activa la trazabilidad de garantia.'
    create_url_name = 'venta_create'
    section = 'ventas'
    search_fields = ['numero_factura', 'cliente__nombre', 'producto__serial']

    def get_queryset(self):
        return super().get_queryset().select_related('cliente', 'producto')


class VentaDetailView(BaseDetailView):
    model = Venta
    title = 'Detalle de venta'
    list_url_name = 'venta_list'
    update_url_name = 'venta_update'
    delete_url_name = 'venta_delete'
    section = 'ventas'
    detail_fields = [
        ('Cliente', 'cliente'),
        ('Producto', 'producto'),
        ('Fecha', 'fecha_venta'),
        ('Valor', 'valor'),
        ('Factura', 'numero_factura'),
        ('Observaciones', 'observaciones'),
    ]


class VentaCreateView(BaseFormView, CreateView):
    model = Venta
    form_class = VentaForm
    title = 'Nueva venta'
    list_url_name = 'venta_list'
    section = 'ventas'


class VentaUpdateView(BaseFormView, UpdateView):
    model = Venta
    form_class = VentaForm
    title = 'Editar venta'
    list_url_name = 'venta_list'
    section = 'ventas'


class VentaDeleteView(BaseDeleteView):
    model = Venta
    success_url = reverse_lazy('venta_list')
    title = 'Eliminar venta'
    list_url_name = 'venta_list'
    section = 'ventas'


class GarantiaListView(BaseListView):
    model = Garantia
    title = 'Garantias'
    subtitle = 'Cobertura, vigencia y condiciones asociadas a cada venta.'
    create_url_name = 'garantia_create'
    section = 'garantias'
    search_fields = ['venta__numero_factura', 'venta__cliente__nombre', 'venta__producto__serial', 'estado']

    def get_queryset(self):
        return super().get_queryset().select_related('venta__cliente', 'venta__producto')


class GarantiaDetailView(BaseDetailView):
    model = Garantia
    title = 'Detalle de garantia'
    list_url_name = 'garantia_list'
    update_url_name = 'garantia_update'
    delete_url_name = 'garantia_delete'
    section = 'garantias'
    detail_fields = [
        ('Venta', 'venta'),
        ('Inicio', 'fecha_inicio'),
        ('Fin', 'fecha_fin'),
        ('Estado', 'get_estado_display'),
        ('Vigente hoy', 'esta_vigente'),
        ('Condiciones', 'condiciones'),
    ]


class GarantiaCreateView(BaseFormView, CreateView):
    model = Garantia
    form_class = GarantiaForm
    title = 'Nueva garantia'
    list_url_name = 'garantia_list'
    section = 'garantias'


class GarantiaUpdateView(BaseFormView, UpdateView):
    model = Garantia
    form_class = GarantiaForm
    title = 'Editar garantia'
    list_url_name = 'garantia_list'
    section = 'garantias'


class GarantiaDeleteView(BaseDeleteView):
    model = Garantia
    success_url = reverse_lazy('garantia_list')
    title = 'Eliminar garantia'
    list_url_name = 'garantia_list'
    section = 'garantias'


class CasoListView(BaseListView):
    model = CasoReparacion
    title = 'Casos tecnicos'
    subtitle = 'Flujo completo de ingreso, revision, reparacion y cierre.'
    create_url_name = 'caso_create'
    section = 'casos'
    search_fields = [
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


class CasoDetailView(BaseDetailView):
    model = CasoReparacion
    title = 'Detalle del caso'
    list_url_name = 'caso_list'
    update_url_name = 'caso_update'
    delete_url_name = 'caso_delete'
    section = 'casos'
    detail_fields = [
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['diagnosticos'] = self.object.diagnosticos.all()[:5]
        context['evidencias'] = self.object.evidencias.all()[:6]
        context['historial'] = self.object.historial_estados.select_related('estado')[:8]
        return context


class CasoCreateView(BaseFormView, CreateView):
    model = CasoReparacion
    form_class = CasoReparacionForm
    title = 'Nuevo caso tecnico'
    list_url_name = 'caso_list'
    section = 'casos'

    def form_valid(self, form):
        response = super().form_valid(form)
        HistorialEstado.objects.create(
            caso=self.object,
            estado=self.object.estado_actual,
            comentario='Apertura del caso tecnico.',
        )
        return response


class CasoUpdateView(BaseFormView, UpdateView):
    model = CasoReparacion
    form_class = CasoReparacionForm
    title = 'Editar caso tecnico'
    list_url_name = 'caso_list'
    section = 'casos'

    def form_valid(self, form):
        estado_anterior = CasoReparacion.objects.get(pk=self.object.pk).estado_actual_id
        if form.instance.estado_actual.es_final and not form.instance.fecha_cierre:
            form.instance.fecha_cierre = timezone.now()
        response = super().form_valid(form)
        if estado_anterior != self.object.estado_actual_id:
            HistorialEstado.objects.create(
                caso=self.object,
                estado=self.object.estado_actual,
                comentario='Cambio de estado desde la edicion del caso.',
            )
        return response


class CasoDeleteView(BaseDeleteView):
    model = CasoReparacion
    success_url = reverse_lazy('caso_list')
    title = 'Eliminar caso tecnico'
    list_url_name = 'caso_list'
    section = 'casos'


class DiagnosticoListView(BaseListView):
    model = Diagnostico
    title = 'Diagnosticos'
    subtitle = 'Analisis tecnicos y soluciones propuestas.'
    create_url_name = 'diagnostico_create'
    section = 'diagnosticos'
    search_fields = ['tecnico', 'diagnostico', 'solucion', 'caso__garantia__venta__cliente__nombre']

    def get_queryset(self):
        return super().get_queryset().select_related('caso__garantia__venta__cliente')


class DiagnosticoDetailView(BaseDetailView):
    model = Diagnostico
    title = 'Detalle de diagnostico'
    list_url_name = 'diagnostico_list'
    update_url_name = 'diagnostico_update'
    delete_url_name = 'diagnostico_delete'
    section = 'diagnosticos'
    detail_fields = [
        ('Caso', 'caso'),
        ('Tecnico', 'tecnico'),
        ('Diagnostico', 'diagnostico'),
        ('Solucion', 'solucion'),
        ('Requiere repuesto', 'requiere_repuesto'),
        ('Costo estimado', 'costo_estimado'),
        ('Fecha', 'fecha'),
    ]


class DiagnosticoCreateView(BaseFormView, CreateView):
    model = Diagnostico
    form_class = DiagnosticoForm
    title = 'Nuevo diagnostico'
    list_url_name = 'diagnostico_list'
    section = 'diagnosticos'


class DiagnosticoUpdateView(BaseFormView, UpdateView):
    model = Diagnostico
    form_class = DiagnosticoForm
    title = 'Editar diagnostico'
    list_url_name = 'diagnostico_list'
    section = 'diagnosticos'


class DiagnosticoDeleteView(BaseDeleteView):
    model = Diagnostico
    success_url = reverse_lazy('diagnostico_list')
    title = 'Eliminar diagnostico'
    list_url_name = 'diagnostico_list'
    section = 'diagnosticos'


class EvidenciaListView(BaseListView):
    model = Evidencia
    title = 'Fotos y evidencias'
    subtitle = 'Archivos de ingreso, reparacion, diagnostico y entrega.'
    create_url_name = 'evidencia_create'
    section = 'evidencias'
    search_fields = ['descripcion', 'tipo', 'caso__garantia__venta__cliente__nombre']

    def get_queryset(self):
        return super().get_queryset().select_related('caso__garantia__venta__cliente')


class EvidenciaDetailView(BaseDetailView):
    model = Evidencia
    title = 'Detalle de evidencia'
    list_url_name = 'evidencia_list'
    update_url_name = 'evidencia_update'
    delete_url_name = 'evidencia_delete'
    section = 'evidencias'
    detail_fields = [
        ('Caso', 'caso'),
        ('Tipo', 'get_tipo_display'),
        ('Descripcion', 'descripcion'),
        ('Fecha', 'fecha'),
    ]


class EvidenciaCreateView(BaseFormView, CreateView):
    model = Evidencia
    form_class = EvidenciaForm
    title = 'Nueva evidencia'
    list_url_name = 'evidencia_list'
    section = 'evidencias'


class EvidenciaUpdateView(BaseFormView, UpdateView):
    model = Evidencia
    form_class = EvidenciaForm
    title = 'Editar evidencia'
    list_url_name = 'evidencia_list'
    section = 'evidencias'


class EvidenciaDeleteView(BaseDeleteView):
    model = Evidencia
    success_url = reverse_lazy('evidencia_list')
    title = 'Eliminar evidencia'
    list_url_name = 'evidencia_list'
    section = 'evidencias'


class EstadoListView(BaseListView):
    model = EstadoCaso
    title = 'Estados'
    subtitle = 'Catalogo del flujo tecnico y de entrega.'
    create_url_name = 'estado_create'
    section = 'estados'
    search_fields = ['codigo', 'nombre', 'descripcion']


class EstadoDetailView(BaseDetailView):
    model = EstadoCaso
    title = 'Detalle de estado'
    list_url_name = 'estado_list'
    update_url_name = 'estado_update'
    delete_url_name = 'estado_delete'
    section = 'estados'
    detail_fields = [
        ('Codigo', 'codigo'),
        ('Nombre', 'nombre'),
        ('Orden', 'orden'),
        ('Final', 'es_final'),
        ('Activo', 'activo'),
        ('Descripcion', 'descripcion'),
    ]


class EstadoCreateView(BaseFormView, CreateView):
    model = EstadoCaso
    form_class = EstadoCasoForm
    title = 'Nuevo estado'
    list_url_name = 'estado_list'
    section = 'estados'


class EstadoUpdateView(BaseFormView, UpdateView):
    model = EstadoCaso
    form_class = EstadoCasoForm
    title = 'Editar estado'
    list_url_name = 'estado_list'
    section = 'estados'


class EstadoDeleteView(BaseDeleteView):
    model = EstadoCaso
    success_url = reverse_lazy('estado_list')
    title = 'Eliminar estado'
    list_url_name = 'estado_list'
    section = 'estados'


class HistorialListView(BaseListView):
    model = HistorialEstado
    title = 'Historial de estados'
    subtitle = 'Auditoria cronologica de cada movimiento del caso.'
    create_url_name = 'historial_create'
    section = 'estados'
    search_fields = ['comentario', 'estado__nombre', 'caso__garantia__venta__cliente__nombre']

    def get_queryset(self):
        return super().get_queryset().select_related('caso', 'estado')


class HistorialDetailView(BaseDetailView):
    model = HistorialEstado
    title = 'Detalle de historial'
    list_url_name = 'historial_list'
    update_url_name = 'historial_update'
    delete_url_name = 'historial_delete'
    section = 'estados'
    detail_fields = [('Caso', 'caso'), ('Estado', 'estado'), ('Fecha', 'fecha'), ('Comentario', 'comentario')]


class HistorialCreateView(BaseFormView, CreateView):
    model = HistorialEstado
    form_class = HistorialEstadoForm
    title = 'Nuevo movimiento'
    list_url_name = 'historial_list'
    section = 'estados'

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.caso.estado_actual = form.instance.estado
        if form.instance.estado.es_final and not form.instance.caso.fecha_cierre:
            form.instance.caso.fecha_cierre = form.instance.fecha
        form.instance.caso.save(update_fields=['estado_actual', 'fecha_cierre', 'actualizado'])
        return response


class HistorialUpdateView(BaseFormView, UpdateView):
    model = HistorialEstado
    form_class = HistorialEstadoForm
    title = 'Editar movimiento'
    list_url_name = 'historial_list'
    section = 'estados'


class HistorialDeleteView(BaseDeleteView):
    model = HistorialEstado
    success_url = reverse_lazy('historial_list')
    title = 'Eliminar movimiento'
    list_url_name = 'historial_list'
    section = 'estados'


class EntregaListView(BaseListView):
    model = Entrega
    title = 'Entregas'
    subtitle = 'Cierre documentado del producto reparado o devuelto.'
    create_url_name = 'entrega_create'
    section = 'entregas'
    search_fields = ['entregado_a', 'documento_entrega', 'caso__garantia__venta__cliente__nombre']

    def get_queryset(self):
        return super().get_queryset().select_related('caso__garantia__venta__cliente')


class EntregaDetailView(BaseDetailView):
    model = Entrega
    title = 'Detalle de entrega'
    list_url_name = 'entrega_list'
    update_url_name = 'entrega_update'
    delete_url_name = 'entrega_delete'
    section = 'entregas'
    detail_fields = [
        ('Caso', 'caso'),
        ('Fecha', 'fecha_entrega'),
        ('Entregado a', 'entregado_a'),
        ('Documento', 'documento_entrega'),
        ('Recibido conforme', 'recibido_conforme'),
        ('Observaciones', 'observaciones'),
    ]


class EntregaCreateView(BaseFormView, CreateView):
    model = Entrega
    form_class = EntregaForm
    title = 'Nueva entrega'
    list_url_name = 'entrega_list'
    section = 'entregas'

    def form_valid(self, form):
        response = super().form_valid(form)
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
        return response


class EntregaUpdateView(BaseFormView, UpdateView):
    model = Entrega
    form_class = EntregaForm
    title = 'Editar entrega'
    list_url_name = 'entrega_list'
    section = 'entregas'


class EntregaDeleteView(BaseDeleteView):
    model = Entrega
    success_url = reverse_lazy('entrega_list')
    title = 'Eliminar entrega'
    list_url_name = 'entrega_list'
    section = 'entregas'


def flujo_rapido(request, caso_id):
    caso = CasoReparacion.objects.get(pk=caso_id)
    siguiente = EstadoCaso.objects.filter(activo=True, orden__gt=caso.estado_actual.orden).order_by('orden').first()
    if siguiente:
        caso.estado_actual = siguiente
        if siguiente.es_final and not caso.fecha_cierre:
            caso.fecha_cierre = timezone.now()
        caso.save(update_fields=['estado_actual', 'fecha_cierre', 'actualizado'])
        HistorialEstado.objects.create(caso=caso, estado=siguiente, comentario='Avance rapido de estado.')
        messages.success(request, f'Caso movido a {siguiente.nombre}.')
    return redirect(caso)

# Create your views here.
