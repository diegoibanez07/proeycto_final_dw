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
