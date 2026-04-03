"""Vistas para el módulo de autenticación."""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import LoginForm


def login_view(request):
    """Vista para iniciar sesión."""
    if request.user.is_authenticated:
        return redirect('rentas:lista')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            nombre = (
                usuario.get_full_name() or usuario.username
            )
            messages.success(
                request,
                f'Bienvenido, {nombre}.',
            )
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            return redirect('rentas:lista')
        else:
            messages.error(
                request,
                'Usuario o contraseña incorrectos.',
            )
    else:
        form = LoginForm(request)

    return render(
        request,
        'authentication/login.html',
        {'form': form},
    )


def logout_view(request):
    """Vista para cerrar sesión."""
    if request.method == 'POST':
        logout(request)
        messages.success(
            request, 'Sesión cerrada correctamente.'
        )
    return redirect('authentication:login')
