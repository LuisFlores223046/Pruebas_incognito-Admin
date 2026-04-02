"""Vistas para el panel de administración."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
from authentication.models import Usuario
from authentication.forms import UsuarioForm, EditarRolForm
from authentication.decorators import admin_required
from solicitudes.models import Solicitud
from solicitudes.services import ejecutar_solicitud
from rentas.models import Renta
from inventario.models import Equipo


@admin_required
def dashboard_admin(request):
    """Panel principal del administrador con métricas del sistema."""
    hoy = date.today()
    limite = hoy + timedelta(days=3)

    total_equipos = Equipo.objects.filter(activo=True).count()
    equipos_disponibles = Equipo.objects.filter(
        activo=True, estado='disponible'
    ).count()
    equipos_rentados = Equipo.objects.filter(
        activo=True, estado='rentado'
    ).count()
    equipos_mantenimiento = Equipo.objects.filter(
        activo=True, estado='mantenimiento'
    ).count()

    total_rentas_activas = Renta.objects.filter(
        estado='activa'
    ).count()
    rentas_por_vencer = Renta.objects.filter(
        estado='activa',
        fecha_vencimiento__gte=hoy,
        fecha_vencimiento__lte=limite,
    ).count()
    rentas_vencidas = Renta.objects.filter(
        estado='activa',
        fecha_vencimiento__lt=hoy,
    ).count()

    solicitudes_pendientes_count = Solicitud.objects.filter(
        estado='pendiente'
    ).count()
    solicitudes_recientes = Solicitud.objects.filter(
        estado='pendiente'
    ).select_related('solicitante', 'equipo').order_by(
        '-fecha_creacion'
    )[:5]

    usuarios_count = Usuario.objects.count()

    contexto = {
        'total_equipos': total_equipos,
        'equipos_disponibles': equipos_disponibles,
        'equipos_rentados': equipos_rentados,
        'equipos_mantenimiento': equipos_mantenimiento,
        'total_rentas_activas': total_rentas_activas,
        'rentas_por_vencer': rentas_por_vencer,
        'rentas_vencidas': rentas_vencidas,
        'solicitudes_pendientes': solicitudes_pendientes_count,
        'solicitudes_recientes': solicitudes_recientes,
        'usuarios_count': usuarios_count,
        'hoy': hoy,
    }
    return render(request, 'panel_admin/dashboard.html', contexto)


@admin_required
def lista_usuarios(request):
    """Lista todos los usuarios del sistema."""
    usuarios = Usuario.objects.all().order_by('username')
    return render(
        request,
        'panel_admin/usuarios_lista.html',
        {'usuarios': usuarios},
    )


@admin_required
def crear_usuario(request):
    """Crea un nuevo usuario (solo admin)."""
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(
                request,
                f'Usuario "{usuario.username}" creado correctamente.',
            )
            return redirect('panel_admin:usuarios')
    else:
        form = UsuarioForm()

    return render(
        request,
        'panel_admin/usuario_form.html',
        {'form': form, 'accion': 'Crear usuario'},
    )


@admin_required
def editar_rol(request, pk):
    """Edita el rol de un usuario (solo admin)."""
    usuario = get_object_or_404(Usuario, pk=pk)

    # No puede cambiar su propio rol
    if usuario == request.user:
        messages.error(
            request,
            'No puedes cambiar tu propio rol.',
        )
        return redirect('panel_admin:usuarios')

    if request.method == 'POST':
        form = EditarRolForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Rol de "{usuario.username}" actualizado a '
                f'{usuario.get_rol_display()}.',
            )
            return redirect('panel_admin:usuarios')
    else:
        form = EditarRolForm(instance=usuario)

    return render(
        request,
        'panel_admin/usuario_form.html',
        {
            'form': form,
            'usuario': usuario,
            'accion': 'Editar rol',
        },
    )


@admin_required
def eliminar_usuario(request, pk):
    """
    Elimina un usuario. Respeta RN-011:
    no permite eliminar al único administrador.
    """
    usuario = get_object_or_404(Usuario, pk=pk)

    # RN-011: no eliminar el único administrador
    if usuario.es_administrador():
        admins_count = Usuario.objects.filter(
            rol='administrador'
        ).count()
        if admins_count <= 1:
            messages.error(
                request,
                'No se puede eliminar al único administrador '
                'del sistema.',
            )
            return redirect('panel_admin:usuarios')

    # No puede eliminarse a sí mismo
    if usuario == request.user:
        messages.error(
            request,
            'No puedes eliminar tu propia cuenta.',
        )
        return redirect('panel_admin:usuarios')

    if request.method == 'POST':
        nombre = usuario.username
        usuario.delete()
        messages.success(
            request,
            f'Usuario "{nombre}" eliminado correctamente.',
        )
        return redirect('panel_admin:usuarios')

    return render(
        request,
        'panel_admin/usuarios_lista.html',
        {'usuario_a_eliminar': usuario},
    )


@admin_required
def solicitudes_pendientes(request):
    """Lista todas las solicitudes pendientes de revisión."""
    solicitudes = Solicitud.objects.filter(
        estado='pendiente'
    ).select_related(
        'solicitante', 'equipo', 'renta'
    ).order_by('-fecha_creacion')

    return render(
        request,
        'panel_admin/solicitudes_lista.html',
        {'solicitudes': solicitudes},
    )


@admin_required
def aprobar_solicitud(request, pk):
    """Aprueba y ejecuta una solicitud pendiente."""
    solicitud = get_object_or_404(
        Solicitud, pk=pk, estado='pendiente'
    )

    if request.method == 'POST':
        try:
            ejecutar_solicitud(solicitud)
            solicitud.resuelto_por = request.user
            solicitud.save()
            messages.success(
                request,
                f'Solicitud #{solicitud.pk} aprobada y ejecutada.',
            )
        except ValueError as e:
            messages.error(request, str(e))
        except Exception:
            messages.error(
                request,
                f'Error al ejecutar la solicitud #{solicitud.pk}.',
            )

    return redirect('panel_admin:solicitudes')


@admin_required
def rechazar_solicitud(request, pk):
    """Rechaza una solicitud pendiente."""
    solicitud = get_object_or_404(
        Solicitud, pk=pk, estado='pendiente'
    )

    if request.method == 'POST':
        solicitud.estado = 'rechazada'
        solicitud.fecha_resolucion = timezone.now()
        solicitud.resuelto_por = request.user
        solicitud.save()
        messages.success(
            request,
            f'Solicitud #{solicitud.pk} rechazada.',
        )

    return redirect('panel_admin:solicitudes')
