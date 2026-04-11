"""
Archivo: views.py
Descripción: Vistas para el panel de administración del sistema RYV Rentas.
             Gestiona el dashboard con métricas generales, la administración
             de usuarios y la revisión de solicitudes pendientes enviadas
             por el Empleado, según lo definido en RF-26, RF-27, RF-28
             y RN-011 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import F, ExpressionWrapper, IntegerField
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
    """
    Muestra el panel principal del Administrador con métricas generales del sistema.

    Calcula y presenta indicadores sobre el estado del inventario, las rentas
    activas, las alertas de vencimiento y las solicitudes pendientes,
    según lo definido en RF-27 y CU-27 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP.

    Retorna:
        HttpResponse: Renderiza la plantilla panel_admin/dashboard.html
        con el contexto de métricas generales del sistema.
    """
    hoy = date.today()
    limite = hoy + timedelta(days=3)

    equipos_activos = Equipo.objects.filter(activo=True)
    total_equipos = equipos_activos.count()

    # estado es propiedad; filtrar con anotaciones ORM
    equipos_disponibles = equipos_activos.annotate(
        calc_disp=ExpressionWrapper(
            F('cantidad_total')
            - F('cantidad_en_renta')
            - F('cantidad_en_mantenimiento'),
            output_field=IntegerField(),
        )
    ).filter(calc_disp__gt=0).count()

    equipos_rentados = equipos_activos.filter(
        cantidad_en_renta__gt=0
    ).count()
    equipos_mantenimiento = equipos_activos.filter(
        cantidad_en_mantenimiento__gt=0
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
    """
    Muestra el listado de todos los usuarios registrados en el sistema.

    Presenta nombre de usuario, rol y fecha de registro de cada usuario,
    según lo definido en RF-26 y CU-28 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP.

    Retorna:
        HttpResponse: Renderiza la plantilla panel_admin/usuarios_lista.html
        con el listado de usuarios ordenado por nombre de usuario.
    """
    usuarios = Usuario.objects.all().order_by('username')
    return render(
        request,
        'panel_admin/usuarios_lista.html',
        {'usuarios': usuarios},
    )


@admin_required
def crear_usuario(request):
    """
    Gestiona el registro de un nuevo usuario en el sistema.

    Solo accesible para el Administrador. Al guardar exitosamente,
    el nuevo usuario puede iniciar sesión con las credenciales asignadas,
    según lo definido en RF-28 y CU-29 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP. En método POST debe
        contener los datos del formulario de creación de usuario.

    Retorna:
        HttpResponse: Redirige al listado de usuarios si el registro
        es exitoso, o renderiza el formulario con errores si falla.
    """
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
    """
    Gestiona el cambio de rol de un usuario existente.

    Solo accesible para el Administrador. Impide que el Administrador
    modifique su propio rol, según lo definido en RF-26 y RN-011 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP. En método POST debe
        contener el nuevo rol seleccionado en el formulario.
        pk (int): Identificador único del usuario a modificar.

    Retorna:
        HttpResponse: Redirige al listado de usuarios si el cambio es exitoso
        o si el Administrador intenta modificar su propio rol, o renderiza
        el formulario con errores si falla.
    """
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
    Gestiona la eliminación de un usuario del sistema.

    Aplica las restricciones RN-011 del SRS que impiden eliminar al único
    Administrador registrado en el sistema, y además impide que el
    Administrador elimine su propia cuenta.

    Parámetros:
        request (HttpRequest): Solicitud HTTP. Debe ser de método POST
        para confirmar y ejecutar la eliminación.
        pk (int): Identificador único del usuario a eliminar.

    Retorna:
        HttpResponse: Redirige al listado de usuarios si la eliminación
        es exitosa o si se viola alguna restricción, o renderiza la
        plantilla de confirmación si la solicitud es GET.
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
    """
    Muestra el listado de todas las solicitudes pendientes de revisión.

    Presenta al Administrador las solicitudes enviadas por el Empleado
    con su tipo, equipo o renta involucrada, comentario y fecha,
    según lo definido en RF-27 y CU-19 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP.

    Retorna:
        HttpResponse: Renderiza la plantilla panel_admin/solicitudes_lista.html
        con el listado de solicitudes pendientes ordenadas por fecha de creación
        descendente.
    """
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
    """
    Aprueba y ejecuta una solicitud pendiente enviada por el Empleado.

    Para solicitudes de cierre de renta, redirige al formulario de devolución
    para capturar la condición del equipo y los datos de pago antes de finalizar.
    Para el resto de tipos, ejecuta la acción correspondiente de forma automática,
    según lo definido en RF-27 y CU-20 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP. Debe ser de método POST
        para confirmar la aprobación.
        pk (int): Identificador único de la solicitud a aprobar.

    Retorna:
        HttpResponse: Redirige al listado de solicitudes al finalizar,
        o al detalle de la renta si es una solicitud de cierre.
    """
    solicitud = get_object_or_404(
        Solicitud, pk=pk, estado='pendiente'
    )

    if request.method == 'POST':
        # Cierre de renta: redirigir al formulario completo para capturar
        # condición del equipo, daños y pago antes de finalizar
        if solicitud.tipo == 'cierre_renta' and solicitud.renta:
            solicitud.estado = 'aprobada'
            solicitud.resuelto_por = request.user
            solicitud.fecha_resolucion = timezone.now()
            solicitud.save()
            messages.info(
                request,
                f'Solicitud #{solicitud.pk} aprobada. '
                'Complete la devolución registrando la condición del equipo.',
            )
            return redirect('rentas:detalle', pk=solicitud.renta.pk)

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
    """
    Rechaza una solicitud pendiente sin ejecutar ninguna acción.

    Marca la solicitud como rechazada y registra al Administrador que
    la resolvió y la fecha de resolución, según lo definido en RF-27
    y CU-21 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP. Debe ser de método POST
        para confirmar el rechazo.
        pk (int): Identificador único de la solicitud a rechazar.

    Retorna:
        HttpResponse: Redirige al listado de solicitudes pendientes.
    """
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
