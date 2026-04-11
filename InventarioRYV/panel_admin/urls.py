"""URLs para el panel de administración."""
from django.urls import path
from . import views

app_name = 'panel_admin'

urlpatterns = [
    path('', views.dashboard_admin, name='dashboard'),
    path('usuarios/', views.lista_usuarios, name='usuarios'),
    path(
        'usuarios/nuevo/',
        views.crear_usuario,
        name='usuario_nuevo',
    ),
    path(
        'usuarios/<int:pk>/editar-rol/',
        views.editar_rol,
        name='editar_rol',
    ),
    path(
        'usuarios/<int:pk>/eliminar/',
        views.eliminar_usuario,
        name='eliminar_usuario',
    ),
    path(
        'solicitudes/',
        views.solicitudes_pendientes,
        name='solicitudes',
    ),
    path(
        'solicitudes/<int:pk>/aprobar/',
        views.aprobar_solicitud,
        name='aprobar',
    ),
    path(
        'solicitudes/<int:pk>/rechazar/',
        views.rechazar_solicitud,
        name='rechazar',
    ),
]
