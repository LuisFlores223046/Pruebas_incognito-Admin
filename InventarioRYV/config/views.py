"""
Archivo: views.py
Descripción: Vistas de manejo de errores HTTP para el sistema RYV Rentas.
             Gestiona las respuestas personalizadas para los errores 403,
             404 y 500, cumpliendo con RNF-010 del SRS que prohíbe exponer
             información técnica interna al usuario.
Fecha: 2026-04-07
Versión: 1.0
"""
from django.shortcuts import render


def error_403(request, exception):
    """
    Maneja el error 403 - Acceso denegado.

    Se activa cuando un usuario autenticado intenta acceder a una vista
    para la que no tiene permisos según su rol, cumpliendo con RF-03
    y RN-008 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP que generó el error.
        exception (Exception): Excepción que desencadenó el error 403.

    Retorna:
        HttpResponse: Renderiza la plantilla 403.html con código de estado 403.
    """
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception):
    """
    Maneja el error 404 - Página no encontrada.

    Se activa cuando el usuario intenta acceder a una URL que no existe
    dentro del sistema.

    Parámetros:
        request (HttpRequest): Solicitud HTTP que generó el error.
        exception (Exception): Excepción que desencadenó el error 404.

    Retorna:
        HttpResponse: Renderiza la plantilla 404.html con código de estado 404.
    """
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    """
    Maneja el error 500 - Error interno del servidor.

    Se activa ante fallos inesperados en el servidor o la base de datos,
    mostrando un mensaje genérico al usuario sin exponer información
    técnica interna, cumpliendo con RNF-010 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP que generó el error.

    Retorna:
        HttpResponse: Renderiza la plantilla 500.html con código de estado 500.
    """
    return render(request, 'errors/500.html', status=500)
