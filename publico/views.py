from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import urlencode

from garantias.models import CasoReparacion, EstadoCaso, Garantia, HistorialEstado

from .forms import FormularioConsultaEstado, FormularioSolicitudServicio


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


def solicitar_servicio(request):
    formulario = FormularioSolicitudServicio(request.POST or None)
    caso_creado = None

    if request.method == 'POST' and formulario.is_valid():
        documento = formulario.cleaned_data['documento'].strip()
        numero_factura = formulario.cleaned_data['numero_factura'].strip()
        garantia = Garantia.objects.select_related(
            'venta__cliente__usuario',
            'venta__producto',
        ).filter(
            venta__cliente__documento=documento,
            venta__numero_factura__iexact=numero_factura,
        ).first()

        if not garantia:
            formulario.add_error(None, 'No encontramos una venta con ese documento y numero de factura.')
        elif garantia.estado == 'anulada':
            formulario.add_error(None, 'La garantia asociada esta anulada. Contacta directamente a la empresa.')
        else:
            estado_recibido = EstadoCaso.objects.get(codigo='recibido')
            caso_creado = CasoReparacion.objects.create(
                garantia=garantia,
                solicitado_por=garantia.venta.cliente.usuario,
                creado_por=garantia.venta.cliente.usuario,
                descripcion_falla=formulario.cleaned_data['descripcion_falla'],
                estado_actual=estado_recibido,
                prioridad='media',
                observaciones='Solicitud creada desde el modulo publico por el cliente.',
            )
            HistorialEstado.objects.create(
                caso=caso_creado,
                estado=estado_recibido,
                comentario='Solicitud publica registrada por el cliente.',
            )
            parametros = urlencode({'documento': documento, 'codigo': caso_creado.id})
            return redirect(f'{reverse("consulta_estado_publico")}?{parametros}')

    return render(request, 'publico/solicitar_servicio.html', {
        'formulario': formulario,
        'caso_creado': caso_creado,
    })

# Create your views here.
