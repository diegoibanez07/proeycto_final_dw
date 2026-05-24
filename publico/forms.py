from django import forms


class FormularioConsultaEstado(forms.Form):
    documento = forms.CharField(
        label='Documento del cliente',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'campo-publico',
            'placeholder': 'Ejemplo: 1000000001',
            'autocomplete': 'on',
            'inputmode': 'numeric',
        }),
    )
    codigo = forms.CharField(
        label='Numero de caso o factura',
        max_length=60,
        widget=forms.TextInput(attrs={
            'class': 'campo-publico',
            'placeholder': 'Ejemplo: 125 o FAC-202605-000125',
            'autocomplete': 'on',
        }),
    )


class FormularioSolicitudServicio(forms.Form):
    documento = forms.CharField(
        label='Documento del cliente',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'campo-publico',
            'placeholder': 'Documento registrado en la compra',
            'autocomplete': 'on',
            'inputmode': 'numeric',
        }),
    )
    numero_factura = forms.CharField(
        label='Numero de factura',
        max_length=60,
        widget=forms.TextInput(attrs={
            'class': 'campo-publico',
            'placeholder': 'Ejemplo: FAC-202605-000125',
            'autocomplete': 'on',
        }),
    )
    descripcion_falla = forms.CharField(
        label='Describe la falla o necesidad',
        max_length=1200,
        widget=forms.Textarea(attrs={
            'class': 'campo-publico area-publica',
            'placeholder': 'Cuenta que ocurre con el producto, desde cuando falla y si tiene accesorios.',
            'rows': 6,
            'autocomplete': 'off',
        }),
    )
