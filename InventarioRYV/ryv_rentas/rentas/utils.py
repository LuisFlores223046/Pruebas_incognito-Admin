"""Utilidades para el módulo de rentas."""
from datetime import date


def marcar_rentas_vencidas():
    """
    Marca como 'vencidas' las rentas activas cuya fecha
    de vencimiento ya pasó. Retorna el conteo de rentas actualizadas.
    """
    from .models import Renta
    vencidas = Renta.objects.filter(
        estado='activa',
        fecha_vencimiento__lt=date.today(),
    )
    count = vencidas.update(estado='vencida')
    return count
