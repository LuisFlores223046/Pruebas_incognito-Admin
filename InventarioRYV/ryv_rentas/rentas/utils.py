"""
Archivo: utils.py
Descripción: Funciones utilitarias para el módulo de rentas del sistema RYV Rentas.
             Provee funciones auxiliares para el mantenimiento automático del
             estado de las rentas, según lo definido en RN-004 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""
from datetime import date


def marcar_rentas_vencidas():
    """
    Marca como 'vencidas' todas las rentas activas cuya fecha de vencimiento ya pasó.

    Ejecuta una actualización masiva en la base de datos para cambiar el estado
    de las rentas activas expiradas, sin cargarlas individualmente en memoria.
    Útil para ejecutarse periódicamente como tarea programada.

    Retorna:
        int: Número de rentas actualizadas a estado 'vencida'.
    """
    from .models import Renta
    vencidas = Renta.objects.filter(
        estado='activa',
        fecha_vencimiento__lt=date.today(),
    )
    count = vencidas.update(estado='vencida')
    return count
