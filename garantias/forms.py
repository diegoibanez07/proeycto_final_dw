from django import forms

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


class FormularioModeloEstilizado(forms.ModelForm):
    def __init__(self, *argumentos, **opciones):
        super().__init__(*argumentos, **opciones)
        for campo in self.fields.values():
            clase_estilo = 'campo-formulario'
            if isinstance(campo.widget, forms.CheckboxInput):
                clase_estilo = 'casilla-formulario'
            elif isinstance(campo.widget, forms.Select):
                clase_estilo = 'selector-formulario'
            elif isinstance(campo.widget, forms.Textarea):
                clase_estilo = 'area-formulario'
                campo.widget.attrs.setdefault('rows', 4)
            clase_actual = campo.widget.attrs.get('class', '')
            campo.widget.attrs['class'] = f'{clase_actual} {clase_estilo}'.strip()


class FormularioCliente(FormularioModeloEstilizado):
    class Meta:
        model = Cliente
        fields = ['tipo_documento', 'documento', 'nombre', 'telefono', 'correo', 'direccion', 'ciudad', 'activo']


class FormularioCategoriaProducto(FormularioModeloEstilizado):
    class Meta:
        model = CategoriaProducto
        fields = ['nombre', 'descripcion', 'activo']


class FormularioProducto(FormularioModeloEstilizado):
    class Meta:
        model = Producto
        fields = ['nombre', 'marca', 'modelo', 'serial', 'categoria', 'descripcion', 'activo']


class FormularioVenta(FormularioModeloEstilizado):
    class Meta:
        model = Venta
        fields = ['cliente', 'producto', 'fecha_venta', 'valor', 'numero_factura', 'observaciones']
        widgets = {'fecha_venta': forms.DateInput(attrs={'type': 'date'})}


class FormularioGarantia(FormularioModeloEstilizado):
    class Meta:
        model = Garantia
        fields = ['venta', 'fecha_inicio', 'fecha_fin', 'estado', 'condiciones']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }


class FormularioEstadoCaso(FormularioModeloEstilizado):
    class Meta:
        model = EstadoCaso
        fields = ['codigo', 'nombre', 'descripcion', 'color', 'orden', 'es_final', 'activo']
        widgets = {'color': forms.TextInput(attrs={'type': 'color'})}


class FormularioCasoReparacion(FormularioModeloEstilizado):
    class Meta:
        model = CasoReparacion
        fields = [
            'garantia',
            'descripcion_falla',
            'estado_actual',
            'prioridad',
            'fecha_ingreso',
            'fecha_cierre',
            'tecnico_responsable',
            'observaciones',
        ]
        widgets = {
            'fecha_ingreso': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_cierre': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class FormularioDiagnostico(FormularioModeloEstilizado):
    class Meta:
        model = Diagnostico
        fields = ['caso', 'tecnico', 'diagnostico', 'solucion', 'requiere_repuesto', 'costo_estimado', 'fecha']
        widgets = {'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'})}


class FormularioEvidencia(FormularioModeloEstilizado):
    class Meta:
        model = Evidencia
        fields = ['caso', 'tipo', 'imagen', 'descripcion', 'fecha']
        widgets = {'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'})}


class FormularioHistorialEstado(FormularioModeloEstilizado):
    class Meta:
        model = HistorialEstado
        fields = ['caso', 'estado', 'fecha', 'comentario']
        widgets = {'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'})}


class FormularioEntrega(FormularioModeloEstilizado):
    class Meta:
        model = Entrega
        fields = ['caso', 'fecha_entrega', 'entregado_a', 'documento_entrega', 'recibido_conforme', 'observaciones']
        widgets = {'fecha_entrega': forms.DateTimeInput(attrs={'type': 'datetime-local'})}
