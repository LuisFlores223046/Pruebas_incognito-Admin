"""Vistas para el módulo de solicitudes."""
from django.shortcuts import render
from authentication.decorators import empleado_o_admin


@empleado_o_admin
def mis_solicitudes(request):
    """Lista las solicitudes enviadas por el usuario actual."""
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
