"""
Archivo: views.py
Descripción: Vistas para el módulo de historial de rentas del sistema RYV Rentas.
             Gestiona la consulta y detalle de rentas finalizadas y vencidas,
             con filtros por cliente, equipo, estado y rango de fechas,
             según lo definido en RF-20 y HU-020 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from rentas.models import Renta
from inventario.models import Equipo
from authentication.decorators import empleado_o_admin


@empleado_o_admin
def historial_lista(request):
    """
    Muestra el listado paginado de rentas finalizadas y vencidas.

    Permite filtrar los resultados por nombre de cliente, nombre de equipo,
    estado de la renta y rango de fechas. Los resultados se ordenan por
    fecha de inicio de forma descendente, según RF-20 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP. Puede incluir los parámetros
        GET: cliente, equipo, estado, fecha_inicio y fecha_fin para filtrar.

    Retorna:
        HttpResponse: Renderiza la plantilla historial/lista.html con el
        listado paginado de rentas y los filtros activos.
    """
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
        'equipos': Equipo.objects.filter(activo=True).order_by('nombre'),
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
    """
    Muestra el detalle completo de una renta del historial.

    Recupera la renta correspondiente al identificador recibido,
    incluyendo los datos del equipo, cliente y usuario que la registró,
    según lo definido en RF-20 y HU-020 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP.
        pk (int): Identificador único de la renta a consultar.

    Retorna:
        HttpResponse: Renderiza la plantilla historial/detalle.html con
        los datos completos de la renta, o devuelve 404 si no existe.
    """
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
