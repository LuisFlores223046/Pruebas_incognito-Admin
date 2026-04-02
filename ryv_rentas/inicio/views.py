"""Vistas para la página de inicio pública."""
from django.shortcuts import render, redirect


def landing(request):
    """Página de bienvenida pública. Redirige si ya hay sesión."""
    if request.user.is_authenticated:
        return redirect('rentas:lista')
    return render(request, 'inicio/landing.html')
