"""Vistas para el módulo de inventario."""
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
    """Lista todos los equipos activos con filtros opcionales."""
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
    """Lista solo los equipos con unidades disponibles."""
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
    """Muestra el detalle completo de un equipo."""
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
    """Crea un nuevo equipo en el inventario (solo admin)."""
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
    """Edita un equipo existente (solo admin). Respeta RN-007."""
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
    """Da de baja un equipo del inventario (solo admin). Respeta RN-006."""
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
    """El empleado solicita un cambio en el inventario (RN-008)."""
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
