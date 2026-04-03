"""Utilidades para el módulo de inventario."""


def actualizar_estado_equipo(equipo):
    """
    Actualiza el estado del equipo basado en sus rentas activas
    y cantidad disponible.
    """
    if equipo.rentas.filter(estado='activa').exists():
        equipo.estado = 'rentado'
    elif equipo.cantidad_disponible == 0:
        equipo.estado = 'mantenimiento'
    else:
        equipo.estado = 'disponible'
    equipo.save(update_fields=['estado'])
