"""Decoradores de control de acceso para RYV Rentas."""
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps


def admin_required(view_func):
    """
    Solo Administradores pueden acceder.
    Lanza PermissionDenied (403) si el usuario no es admin.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        """Verifica que el usuario sea administrador."""
        if not request.user.es_administrador():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def empleado_o_admin(view_func):
    """Cualquier usuario autenticado puede acceder."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        """Verifica que el usuario esté autenticado."""
        return view_func(request, *args, **kwargs)
    return wrapper
