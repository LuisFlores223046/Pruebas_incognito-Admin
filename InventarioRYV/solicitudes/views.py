"""
Archivo: views.py
Descripción: Vistas para el módulo de solicitudes del sistema RYV Rentas.
             Gestiona la consulta de solicitudes enviadas por el usuario
             autenticado, según lo definido en RF-27 y CU-18 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""
from django.shortcuts import render
from authentication.decorators import empleado_o_admin


@empleado_o_admin
def mis_solicitudes(request):
    """
    Muestra el listado de solicitudes enviadas por el usuario autenticado.

    Permite que tanto el Empleado como el Administrador consulten el estado
    de sus propias solicitudes, ordenadas por fecha de creación descendente,
    según lo definido en CU-18 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP.

    Retorna:
        HttpResponse: Renderiza la plantilla panel_admin/solicitudes_lista.html
        con el listado de solicitudes del usuario autenticado.
    """
    from .models import Solicitud
    solicitudes = Solicitud.objects.filter(
        solicitante=request.user
    ).select_related(
        'equipo', 'renta', 'resuelto_por'
    ).order_by('-fecha_creacion')

    contexto = {
        'solicitudes': solicitudes,
        'mis_solicitudes': True,
    }
    return render(
        request,
        'panel_admin/solicitudes_lista.html',
        contexto,
    )
