from django.db.models import Q
from django.shortcuts import render

from garantias.models import CasoReparacion

from .forms import FormularioConsultaEstado


def inicio_publico(request):
    return render(request, 'publico/inicio.html')


def servicios_publicos(request):
    return render(request, 'publico/servicios.html')


def consulta_estado(request):
    formulario = FormularioConsultaEstado(request.GET or None)
    caso = None
    busqueda_realizada = False

    if formulario.is_valid():
        busqueda_realizada = True
        documento = formulario.cleaned_data['documento'].strip()
        codigo = formulario.cleaned_data['codigo'].strip()
        filtros_codigo = Q(garantia__venta__numero_factura__iexact=codigo)
        if codigo.isdigit():
            filtros_codigo |= Q(id=int(codigo))

        caso = CasoReparacion.objects.select_related(
            'garantia__venta__cliente',
            'garantia__venta__producto',
            'estado_actual',
        ).filter(
            garantia__venta__cliente__documento=documento,
        ).filter(filtros_codigo).order_by('-fecha_ingreso').first()

    return render(request, 'publico/consulta_estado.html', {
        'formulario': formulario,
        'caso': caso,
        'busqueda_realizada': busqueda_realizada,
    })

# Create your views here.
