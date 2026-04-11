"""
Archivo: views.py
Descripción: Vistas para el módulo de autenticación del sistema RYV Rentas.
             Gestiona el inicio y cierre de sesión de los usuarios,
             según lo definido en RF-01 y RF-02 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import LoginForm


def login_view(request):
    """
    Gestiona el inicio de sesión de un usuario en el sistema.

    Si el usuario ya está autenticado, redirige directamente al listado
    de rentas. Si las credenciales son incorrectas, muestra un mensaje
    de error y vuelve a presentar el formulario.

    Args:
        request (HttpRequest): Solicitud HTTP. En método POST debe
        contener los campos de usuario y contraseña del formulario.

    Returns:
        HttpResponse: Redirige al listado de rentas si el login es exitoso,
        o renderiza el formulario de login con mensajes de error si falla.
    """
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
    """
    Gestiona el cierre de sesión de un usuario autenticado.

    Solo procesa el cierre de sesión si la solicitud es POST,
    invalidando la sesión activa en el servidor y redirigiendo
    al login, según lo definido en RF-02 del SRS.

    Args:
        request (HttpRequest): Solicitud HTTP. Debe ser de método POST
        para ejecutar el cierre de sesión.

    Returns:
        HttpResponse: Redirige a la pantalla de login en todos los casos.
    """
    if request.method == 'POST':
        logout(request)
        messages.success(
            request, 'Sesión cerrada correctamente.'
        )
    return redirect('authentication:login')
