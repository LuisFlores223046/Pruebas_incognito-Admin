"""Context processors globales para RYV Rentas."""


def alertas_globales(request):
    """
    Inyecta en TODOS los templates:
    - alertas_proximas: rentas a 3 días o menos de vencer
    - alertas_vencidas: rentas ya vencidas sin cerrar
    - solicitudes_pendientes: conteo para el panel admin
    """
    if not request.user.is_authenticated:
        return {}

    from rentas.models import Renta
    from solicitudes.models import Solicitud
    from datetime import date, timedelta

    hoy = date.today()
    limite = hoy + timedelta(days=3)

    rentas_activas = Renta.objects.filter(estado='activa')

    alertas_proximas = rentas_activas.filter(
        fecha_vencimiento__gte=hoy,
        fecha_vencimiento__lte=limite
    ).select_related('equipo', 'cliente')

    alertas_vencidas = rentas_activas.filter(
        fecha_vencimiento__lt=hoy
    ).select_related('equipo', 'cliente')

    solicitudes_pendientes = 0
    if request.user.es_administrador():
        solicitudes_pendientes = Solicitud.objects.filter(
            estado='pendiente'
        ).count()

    return {
        'alertas_proximas': alertas_proximas,
        'alertas_vencidas': alertas_vencidas,
        'total_alertas': (
            alertas_proximas.count() + alertas_vencidas.count()
        ),
        'solicitudes_pendientes': solicitudes_pendientes,
    }
