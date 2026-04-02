"""Vistas para el módulo de historial de rentas."""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from rentas.models import Renta
from authentication.decorators import empleado_o_admin


@empleado_o_admin
def historial_lista(request):
    """Lista el historial de rentas finalizadas y vencidas."""
    rentas = Renta.objects.exclude(
        estado='activa'
    ).select_related('equipo', 'cliente', 'registrada_por')

    # Filtros
    cliente_nombre = request.GET.get('cliente', '').strip()
    equipo_nombre = request.GET.get('equipo', '').strip()
    estado = request.GET.get('estado', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    if cliente_nombre:
        rentas = rentas.filter(
            cliente__nombre__icontains=cliente_nombre
        )
    if equipo_nombre:
        rentas = rentas.filter(
            equipo__nombre__icontains=equipo_nombre
        )
    if estado:
        rentas = rentas.filter(estado=estado)
    if fecha_inicio:
        rentas = rentas.filter(fecha_inicio__gte=fecha_inicio)
    if fecha_fin:
        rentas = rentas.filter(fecha_inicio__lte=fecha_fin)

    rentas = rentas.order_by('-fecha_inicio')

    paginator = Paginator(rentas, 20)
    page = request.GET.get('page', 1)
    rentas_page = paginator.get_page(page)

    contexto = {
        'rentas': rentas_page,
        'filtro_cliente': cliente_nombre,
        'filtro_equipo': equipo_nombre,
        'filtro_estado': estado,
        'filtro_fecha_inicio': fecha_inicio,
        'filtro_fecha_fin': fecha_fin,
        'estados': [
            ('finalizada', 'Finalizada'),
            ('vencida', 'Vencida'),
        ],
    }
    return render(request, 'historial/lista.html', contexto)


@empleado_o_admin
def historial_detalle(request, pk):
    """Muestra el detalle de una renta del historial."""
    renta = get_object_or_404(
        Renta.objects.select_related(
            'equipo', 'cliente', 'registrada_por'
        ),
        pk=pk,
    )
    return render(
        request,
        'historial/detalle.html',
        {'renta': renta},
    )
