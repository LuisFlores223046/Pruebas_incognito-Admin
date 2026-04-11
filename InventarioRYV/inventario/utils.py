"""
Archivo: utils.py
Descripción: Funciones utilitarias para el módulo de inventario del sistema RYV Rentas.
             Provee funciones auxiliares para la gestión del estado de los equipos,
             según lo definido en RN-002 y RN-003 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""

def actualizar_estado_equipo(equipo):
    """
    Actualiza el estado de un equipo según sus rentas activas y disponibilidad.

    Evalúa si el equipo tiene rentas activas o unidades disponibles para
    determinar su estado actual y persistirlo en la base de datos, cumpliendo
    con RN-002 y RN-003 del SRS que exigen la actualización automática del
    estado al crear o finalizar una renta.

    Parámetros:
        equipo (Equipo): Instancia del modelo Equipo cuyo estado se actualizará.

    Retorna:
        None
    """
    if equipo.rentas.filter(estado='activa').exists():
        equipo.estado = 'rentado'
    elif equipo.cantidad_disponible == 0:
        equipo.estado = 'mantenimiento'
    else:
        equipo.estado = 'disponible'
    equipo.save(update_fields=['estado'])
