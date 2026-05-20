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


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = 'form-input'
            if isinstance(field.widget, forms.CheckboxInput):
                css_class = 'form-check'
            elif isinstance(field.widget, forms.Select):
                css_class = 'form-select'
            elif isinstance(field.widget, forms.Textarea):
                css_class = 'form-textarea'
                field.widget.attrs.setdefault('rows', 4)
            field.widget.attrs['class'] = f"{field.widget.attrs.get('class', '')} {css_class}".strip()


class ClienteForm(StyledModelForm):
    class Meta:
        model = Cliente
        fields = ['tipo_documento', 'documento', 'nombre', 'telefono', 'correo', 'direccion', 'ciudad', 'activo']


class CategoriaProductoForm(StyledModelForm):
    class Meta:
        model = CategoriaProducto
        fields = ['nombre', 'descripcion', 'activo']


class ProductoForm(StyledModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'marca', 'modelo', 'serial', 'categoria', 'descripcion', 'activo']


class VentaForm(StyledModelForm):
    class Meta:
        model = Venta
        fields = ['cliente', 'producto', 'fecha_venta', 'valor', 'numero_factura', 'observaciones']
        widgets = {'fecha_venta': forms.DateInput(attrs={'type': 'date'})}


class GarantiaForm(StyledModelForm):
    class Meta:
        model = Garantia
        fields = ['venta', 'fecha_inicio', 'fecha_fin', 'estado', 'condiciones']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }


class EstadoCasoForm(StyledModelForm):
    class Meta:
        model = EstadoCaso
        fields = ['codigo', 'nombre', 'descripcion', 'color', 'orden', 'es_final', 'activo']
        widgets = {'color': forms.TextInput(attrs={'type': 'color'})}


class CasoReparacionForm(StyledModelForm):
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


class DiagnosticoForm(StyledModelForm):
    class Meta:
        model = Diagnostico
        fields = ['caso', 'tecnico', 'diagnostico', 'solucion', 'requiere_repuesto', 'costo_estimado', 'fecha']
        widgets = {'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'})}


class EvidenciaForm(StyledModelForm):
    class Meta:
        model = Evidencia
        fields = ['caso', 'tipo', 'imagen', 'descripcion', 'fecha']
        widgets = {'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'})}


class HistorialEstadoForm(StyledModelForm):
    class Meta:
        model = HistorialEstado
        fields = ['caso', 'estado', 'fecha', 'comentario']
        widgets = {'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'})}


class EntregaForm(StyledModelForm):
    class Meta:
        model = Entrega
        fields = ['caso', 'fecha_entrega', 'entregado_a', 'documento_entrega', 'recibido_conforme', 'observaciones']
        widgets = {'fecha_entrega': forms.DateTimeInput(attrs={'type': 'datetime-local'})}
