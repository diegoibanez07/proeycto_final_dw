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


AUTOCOMPLETADO_POR_CAMPO = {
    'documento': 'on',
    'documento_entrega': 'on',
    'nombre': 'name',
    'telefono': 'tel',
    'correo': 'email',
    'direccion': 'street-address',
    'ciudad': 'address-level2',
    'marca': 'organization',
    'modelo': 'on',
    'serial': 'on',
    'numero_factura': 'on',
    'tecnico': 'name',
    'tecnico_responsable': 'name',
    'entregado_a': 'name',
    'codigo': 'on',
    'color': 'off',
}

AYUDAS_POR_CAMPO = {
    'cliente': 'Busca por nombre, documento o correo.',
    'producto': 'Busca por producto, marca, modelo o serial.',
    'venta': 'Busca por factura, cliente o producto.',
    'garantia': 'Busca por factura, cliente, producto o estado.',
    'caso': 'Busca por numero de caso, cliente, producto o serial.',
    'estado_actual': 'Busca y selecciona el estado actual del caso.',
    'estado': 'Busca y selecciona el estado correspondiente.',
    'categoria': 'Busca o selecciona la categoria del producto.',
}

PLACEHOLDERS_POR_CAMPO = {
    'documento': 'Documento del cliente',
    'documento_entrega': 'Documento de quien recibe',
    'nombre': 'Nombre completo o nombre del registro',
    'telefono': '3001234567',
    'correo': 'cliente@correo.com',
    'direccion': 'Direccion completa',
    'ciudad': 'Ciudad',
    'marca': 'Marca',
    'modelo': 'Modelo',
    'serial': 'Serial unico del producto',
    'numero_factura': 'Numero de factura',
    'descripcion': 'Descripcion clara del registro',
    'descripcion_falla': 'Describe la falla reportada por el cliente',
    'diagnostico': 'Describe el diagnostico tecnico',
    'solucion': 'Describe la solucion aplicada o recomendada',
    'observaciones': 'Observaciones importantes',
    'condiciones': 'Condiciones de la garantia',
    'comentario': 'Comentario del cambio de estado',
    'tecnico': 'Nombre del tecnico',
    'tecnico_responsable': 'Nombre del tecnico responsable',
    'entregado_a': 'Nombre de quien recibe',
    'codigo': 'codigo-del-estado',
}


class FormularioModeloEstilizado(forms.ModelForm):
    def __init__(self, *argumentos, **opciones):
        super().__init__(*argumentos, **opciones)
        for nombre_campo, campo in self.fields.items():
            clase_estilo = 'campo-formulario'
            if isinstance(campo.widget, forms.CheckboxInput):
                clase_estilo = 'casilla-formulario'
            elif isinstance(campo.widget, forms.Select):
                clase_estilo = 'selector-formulario'
                if not isinstance(campo.widget, forms.SelectMultiple):
                    clase_estilo = 'selector-formulario selector-autocomplete'
                    campo.widget.attrs.setdefault('data-autocomplete', 'true')
                    campo.widget.attrs.setdefault(
                        'data-placeholder',
                        f'Buscar {campo.label.lower()}...',
                    )
                    campo.help_text = campo.help_text or AYUDAS_POR_CAMPO.get(nombre_campo, 'Puedes escribir para buscar una opcion.')
            elif isinstance(campo.widget, forms.Textarea):
                clase_estilo = 'area-formulario'
                campo.widget.attrs.setdefault('rows', 4)
                campo.widget.attrs.setdefault('spellcheck', 'true')
            else:
                campo.widget.attrs.setdefault('autocomplete', AUTOCOMPLETADO_POR_CAMPO.get(nombre_campo, 'on'))

            if nombre_campo in PLACEHOLDERS_POR_CAMPO and not isinstance(campo.widget, forms.Select):
                campo.widget.attrs.setdefault('placeholder', PLACEHOLDERS_POR_CAMPO[nombre_campo])

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
