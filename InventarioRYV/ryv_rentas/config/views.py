"""Vistas de manejo de errores HTTP para RYV Rentas."""
from django.shortcuts import render


def error_403(request, exception):
    """Vista para error 403 - Acceso denegado."""
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception):
    """Vista para error 404 - Página no encontrada."""
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    """Vista para error 500 - Error interno del servidor."""
    return render(request, 'errors/500.html', status=500)
