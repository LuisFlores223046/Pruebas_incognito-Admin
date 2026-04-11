"""
Archivo: views.py
Descripción: Vistas para el módulo de inventario del sistema RYV Rentas.
             Gestiona el listado, detalle, creación, edición y baja de equipos,
             así como las solicitudes de cambio enviadas por el Empleado,
             según lo definido en RF-05 al RF-12 y RN-006, RN-007, RN-008 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import F, ExpressionWrapper, IntegerField
from .models import Equipo
from .forms import EquipoForm, SolicitudEquipoForm
from authentication.decorators import admin_required, empleado_o_admin
from solicitudes.models import Solicitud


@empleado_o_admin
def lista_inventario(request):
    """
    Muestra el listado paginado de todos los equipos activos del inventario.

    Permite filtrar los resultados por nombre del equipo mediante el
    parámetro GET 'nombre', según lo definido en RF-07 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP. Puede incluir el parámetro
        GET 'nombre' para filtrar equipos por nombre.

    Retorna:
        HttpResponse: Renderiza la plantilla inventario/lista.html con
        el listado paginado de equipos y el filtro activo.
    """
    equipos = Equipo.objects.filter(activo=True)

    nombre = request.GET.get('nombre', '').strip()
    if nombre:
        equipos = equipos.filter(nombre__icontains=nombre)

    paginator = Paginator(equipos, 20)
    page = request.GET.get('page', 1)
    equipos_page = paginator.get_page(page)

    contexto = {
        'equipos': equipos_page,
        'filtro_nombre': nombre,
    }
    return render(request, 'inventario/lista.html', contexto)


@empleado_o_admin
def disponibles_view(request):
    """
    Muestra el listado paginado de equipos con al menos una unidad disponible.

    Calcula la disponibilidad en la base de datos mediante anotación para
    evitar cargar todos los equipos en memoria. Permite filtrar por nombre,
    según lo definido en RF-07 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP. Puede incluir el parámetro
        GET 'nombre' para filtrar equipos por nombre.

    Retorna:
        HttpResponse: Renderiza la plantilla inventario/disponibles.html
        con el listado paginado de equipos disponibles y el filtro activo.
    """
    equipos = Equipo.objects.filter(activo=True).annotate(
        calc_disp=ExpressionWrapper(
            F('cantidad_total')
            - F('cantidad_en_renta')
            - F('cantidad_en_mantenimiento'),
            output_field=IntegerField(),
        )
    ).filter(calc_disp__gt=0).order_by('nombre')

    nombre = request.GET.get('nombre', '').strip()
    if nombre:
        equipos = equipos.filter(nombre__icontains=nombre)

    paginator = Paginator(equipos, 20)
    page = request.GET.get('page', 1)
    equipos_page = paginator.get_page(page)

    contexto = {
        'equipos': equipos_page,
        'filtro_nombre': nombre,
    }
    return render(request, 'inventario/disponibles.html', contexto)


@empleado_o_admin
def detalle_equipo(request, pk):
    """
    Muestra el detalle completo de un equipo activo del inventario.

    Incluye las rentas activas asociadas al equipo para que el usuario
    pueda conocer su estado actual, según lo definido en RF-08 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP.
        pk (int): Identificador único del equipo a consultar.

    Retorna:
        HttpResponse: Renderiza la plantilla inventario/detalle.html con
        los datos del equipo y sus rentas activas, o devuelve 404 si no existe.
    """
    equipo = get_object_or_404(Equipo, pk=pk, activo=True)
    rentas_activas = equipo.rentas.filter(
        estado='activa'
    ).select_related('cliente')

    contexto = {
        'equipo': equipo,
        'rentas_activas': rentas_activas,
    }
    return render(request, 'inventario/detalle.html', contexto)


@admin_required
def crear_equipo(request):
    """
    Gestiona el registro de un nuevo equipo en el inventario.

    Solo accesible para el Administrador. Al guardar exitosamente,
    el equipo queda registrado con estado 'Disponible' y visible
    para todos los usuarios, según lo definido en RF-05 del SRS.

    Parámetros:
        request (HttpRequest): Solicitud HTTP. En método POST debe
        contener los datos del formulario de creación de equipo.

    Retorna:
        HttpResponse: Redirige al listado de inventario si el registro
        es exitoso, o renderiza el formulario con errores si falla.
    """
    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES)
        if form.is_valid():
            equipo = form.save()
            messages.success(
                request,
                f'Equipo "{equipo.nombre}" creado correctamente.',
            )
            return redirect('inventario:lista')
    else:
        form = EquipoForm()

    return render(request, 'inventario/crear.html', {'form': form})


@admin_required
def editar_equipo(request, pk):
    """
    Gestiona la edición de la información de un equipo existente.

    Solo accesible para el Administrador. Aplica la restricción RN-007
    del SRS que impide reducir la cantidad total por debajo del número
    de unidades actualmente en renta activa.

    Parámetros:
        request (HttpRequest): Solicitud HTTP. En método POST debe
        contener los datos actualizados del formulario de edición.
        pk (int): Identificador único del equipo a editar.

    Retorna:
        HttpResponse: Redirige al detalle del equipo si la edición es exitosa,
        o renderiza el formulario con errores si falla o viola RN-007.
    """
    equipo = get_object_or_404(Equipo, pk=pk, activo=True)
    tiene_renta = equipo.tiene_renta_activa()

    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES, instance=equipo)
        if form.is_valid():
            # RN-007: No reducir el total por debajo de lo rentado
            if tiene_renta:
                nuevo_total = form.cleaned_data.get('cantidad_total', equipo.cantidad_total)
                if nuevo_total < equipo.cantidad_en_renta:
                    messages.error(
                        request,
                        f'No se puede reducir la cantidad total a {nuevo_total} '
                        f'porque hay {equipo.cantidad_en_renta} unidad(es) en renta activa.',
                    )
                    contexto = {
                        'form': form,
                        'equipo': equipo,
                        'tiene_renta': tiene_renta,
                    }
                    return render(
                        request,
                        'inventario/editar.html',
                        contexto,
                    )
            form.save()
            messages.success(
                request,
                f'Equipo "{equipo.nombre}" actualizado correctamente.',
            )
            return redirect('inventario:detalle', pk=equipo.pk)
    else:
        form = EquipoForm(instance=equipo)

    contexto = {
        'form': form,
        'equipo': equipo,
        'tiene_renta': tiene_renta,
    }
    return render(request, 'inventario/editar.html', contexto)


@admin_required
def dar_baja_equipo(request, pk):
    """
    Gestiona la baja de un equipo del inventario.

    Solo accesible para el Administrador. Aplica la restricción RN-006
    del SRS que impide dar de baja un equipo con unidades actualmente
    en renta activa. La baja es lógica: el equipo se marca como inactivo
    pero no se elimina de la base de datos.

    Parámetros:
        request (HttpRequest): Solicitud HTTP. Debe ser de método POST
        para confirmar y ejecutar la baja.
        pk (int): Identificador único del equipo a dar de baja.

    Retorna:
        HttpResponse: Redirige al listado de inventario si la baja es exitosa,
        redirige al detalle con mensaje de error si el equipo tiene rentas activas,
        o renderiza la plantilla de confirmación si la solicitud es GET.
    """
    equipo = get_object_or_404(Equipo, pk=pk, activo=True)

    if equipo.tiene_renta_activa():
        messages.error(
            request,
            f'No se puede dar de baja "{equipo.nombre}" porque '
            f'tiene {equipo.cantidad_en_renta} unidad(es) en renta activa. '
            'Finaliza las rentas primero.',
        )
        return redirect('inventario:detalle', pk=equipo.pk)

    if request.method == 'POST':
        nombre = equipo.nombre
        equipo.activo = False
        equipo.save()
        messages.success(
            request,
            f'Equipo "{nombre}" dado de baja correctamente.',
        )
        return redirect('inventario:lista')

    contexto = {
        'equipo': equipo,
        'confirmar_baja': True,
    }
    return render(request, 'inventario/detalle.html', contexto)


@empleado_o_admin
def solicitar_cambio(request):
    """
    Gestiona el envío de solicitudes de cambio en el inventario por parte del Empleado.

    Permite al Empleado solicitar el alta, edición o baja de un equipo.
    La solicitud queda pendiente hasta que el Administrador la apruebe
    o rechace desde el panel de solicitudes, cumpliendo con RN-008 del SRS.
    Si el usuario es Administrador, lo redirige a realizar el cambio directamente.

    Parámetros:
        request (HttpRequest): Solicitud HTTP. Puede incluir el parámetro
        GET 'equipo' para preseleccionar un equipo en el formulario. En método
        POST debe contener los datos de la solicitud.

    Retorna:
        HttpResponse: Redirige al listado de inventario si la solicitud se envía
        exitosamente o si el usuario es Administrador, o renderiza el formulario
        de solicitud con los datos del equipo preseleccionado si falla.
    """
    import json
    from django.core.serializers.json import DjangoJSONEncoder

    if request.user.es_administrador():
        messages.info(
            request,
            'Como administrador, puedes realizar cambios directamente.',
        )
        return redirect('inventario:lista')

    equipo_pk = request.GET.get('equipo')
    equipo_preseleccionado = None
    if equipo_pk:
        equipo_preseleccionado = get_object_or_404(
            Equipo, pk=equipo_pk, activo=True
        )

    # Datos de equipos para pre-poblar campos vía JS
    equipos_data = list(
        Equipo.objects.filter(activo=True).order_by('nombre').values(
            'id', 'nombre', 'descripcion',
            'cantidad_total', 'cantidad_en_mantenimiento', 'cantidad_en_renta',
        )
    )

    if request.method == 'POST':
        form = SolicitudEquipoForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            comentario = form.cleaned_data['comentario']
            equipo_seleccionado = form.cleaned_data.get('equipo_existente')

            datos_json = {}
            if tipo == 'alta_equipo':
                datos_json = {
                    'nombre': form.cleaned_data.get('nombre_equipo', ''),
                    'descripcion': form.cleaned_data.get('descripcion_equipo', ''),
                    'cantidad_total': form.cleaned_data.get('cantidad_total', 1) or 1,
                }
            elif tipo == 'edicion_equipo' and equipo_seleccionado:
                datos_json = {
                    'nombre': form.cleaned_data.get('nombre_equipo', ''),
                    'descripcion': form.cleaned_data.get('descripcion_equipo', ''),
                    'cantidad_total': form.cleaned_data.get('cantidad_total'),
                }
            elif tipo == 'baja_equipo' and equipo_seleccionado:
                datos_json = {
                    'cantidad_baja': form.cleaned_data.get('cantidad_baja', 1) or 1,
                }

            Solicitud.objects.create(
                tipo=tipo,
                solicitante=request.user,
                equipo=equipo_seleccionado,
                comentario=comentario,
                datos_json=datos_json,
            )
            messages.success(
                request,
                'Solicitud enviada. El administrador la revisará pronto.',
            )
            return redirect('inventario:lista')
    else:
        initial = {}
        if equipo_preseleccionado:
            initial['equipo_existente'] = equipo_preseleccionado
        form = SolicitudEquipoForm(initial=initial)

    contexto = {
        'form': form,
        'equipo_preseleccionado': equipo_preseleccionado,
        'equipos_json': json.dumps(equipos_data, cls=DjangoJSONEncoder),
    }
    return render(
        request,
        'inventario/solicitar_cambio.html',
        contexto,
    )
