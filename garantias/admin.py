from django.contrib import admin

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


@admin.register(Cliente)
class AdministradorCliente(admin.ModelAdmin):
    list_display = ('nombre', 'documento', 'telefono', 'correo', 'activo')
    search_fields = ('nombre', 'documento', 'telefono', 'correo')
    list_filter = ('activo', 'tipo_documento')


@admin.register(CategoriaProducto)
class AdministradorCategoriaProducto(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)


@admin.register(Producto)
class AdministradorProducto(admin.ModelAdmin):
    list_display = ('nombre', 'marca', 'modelo', 'serial', 'categoria', 'activo')
    search_fields = ('nombre', 'marca', 'modelo', 'serial')
    list_filter = ('categoria', 'activo')


@admin.register(Venta)
class AdministradorVenta(admin.ModelAdmin):
    list_display = ('numero_factura', 'cliente', 'producto', 'fecha_venta', 'valor')
    search_fields = ('numero_factura', 'cliente__nombre', 'producto__serial')
    list_filter = ('fecha_venta',)


@admin.register(Garantia)
class AdministradorGarantia(admin.ModelAdmin):
    list_display = ('venta', 'fecha_inicio', 'fecha_fin', 'estado')
    search_fields = ('venta__numero_factura', 'venta__cliente__nombre')
    list_filter = ('estado', 'fecha_fin')


@admin.register(EstadoCaso)
class AdministradorEstadoCaso(admin.ModelAdmin):
    list_display = ('orden', 'nombre', 'codigo', 'es_final', 'activo')
    list_display_links = ('nombre',)
    list_editable = ('orden', 'es_final', 'activo')
    search_fields = ('nombre', 'codigo')


@admin.register(CasoReparacion)
class AdministradorCasoReparacion(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'producto', 'estado_actual', 'prioridad', 'fecha_ingreso', 'fecha_cierre')
    search_fields = (
        'garantia__venta__cliente__nombre',
        'garantia__venta__producto__serial',
        'descripcion_falla',
        'tecnico_responsable',
    )
    list_filter = ('estado_actual', 'prioridad', 'fecha_ingreso')


@admin.register(Diagnostico)
class AdministradorDiagnostico(admin.ModelAdmin):
    list_display = ('caso', 'tecnico', 'requiere_repuesto', 'costo_estimado', 'fecha')
    search_fields = ('tecnico', 'diagnostico', 'solucion')
    list_filter = ('requiere_repuesto', 'fecha')


@admin.register(Evidencia)
class AdministradorEvidencia(admin.ModelAdmin):
    list_display = ('caso', 'tipo', 'descripcion', 'fecha')
    search_fields = ('descripcion', 'caso__garantia__venta__cliente__nombre')
    list_filter = ('tipo', 'fecha')


@admin.register(HistorialEstado)
class AdministradorHistorialEstado(admin.ModelAdmin):
    list_display = ('caso', 'estado', 'fecha', 'comentario')
    search_fields = ('comentario', 'estado__nombre')
    list_filter = ('estado', 'fecha')


@admin.register(Entrega)
class AdministradorEntrega(admin.ModelAdmin):
    list_display = ('caso', 'entregado_a', 'documento_entrega', 'fecha_entrega', 'recibido_conforme')
    search_fields = ('entregado_a', 'documento_entrega', 'caso__garantia__venta__cliente__nombre')
    list_filter = ('recibido_conforme', 'fecha_entrega')

# Register your models here.
