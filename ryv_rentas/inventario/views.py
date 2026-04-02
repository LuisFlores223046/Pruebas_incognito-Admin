"""Vistas para el módulo de inventario."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Equipo, Categoria
from .forms import EquipoForm, SolicitudEquipoForm
from authentication.decorators import admin_required, empleado_o_admin
from solicitudes.models import Solicitud


@empleado_o_admin
def lista_inventario(request):
    """Lista todos los equipos activos con filtros opcionales."""
    equipos = Equipo.objects.filter(
        activo=True
    ).select_related('categoria')

    # Filtros por GET
    nombre = request.GET.get('nombre', '').strip()
    categoria_id = request.GET.get('categoria', '')
    estado = request.GET.get('estado', '')

    if nombre:
        equipos = equipos.filter(nombre__icontains=nombre)
    if categoria_id:
        equipos = equipos.filter(categoria_id=categoria_id)
    if estado:
        equipos = equipos.filter(estado=estado)

    # Paginación
    paginator = Paginator(equipos, 20)
    page = request.GET.get('page', 1)
    equipos_page = paginator.get_page(page)

    categorias = Categoria.objects.all()
    estados = Equipo.ESTADO_CHOICES

    contexto = {
        'equipos': equipos_page,
        'categorias': categorias,
        'estados': estados,
        'filtro_nombre': nombre,
        'filtro_categoria': categoria_id,
        'filtro_estado': estado,
    }
    return render(request, 'inventario/lista.html', contexto)


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
        form = EquipoForm(request.POST)
        if form.is_valid():
            equipo = form.save()
            messages.success(
                request,
                f'Equipo "{equipo.nombre}" creado correctamente.',
            )
            return redirect('inventario:detalle', pk=equipo.pk)
    else:
        form = EquipoForm()

    return render(request, 'inventario/crear.html', {'form': form})


@admin_required
def editar_equipo(request, pk):
    """Edita un equipo existente (solo admin). Respeta RN-007."""
    equipo = get_object_or_404(Equipo, pk=pk, activo=True)
    tiene_renta = equipo.tiene_renta_activa()

    if request.method == 'POST':
        form = EquipoForm(request.POST, instance=equipo)
        if form.is_valid():
            # RN-007: No modificar campos críticos con renta activa
            if tiene_renta:
                nombre_cambiado = (
                    form.cleaned_data['nombre'] != equipo.nombre
                )
                cat_cambiada = (
                    form.cleaned_data.get('categoria')
                    != equipo.categoria
                )
                if nombre_cambiado or cat_cambiada:
                    messages.error(
                        request,
                        'No se puede modificar nombre o categoría '
                        'mientras el equipo tiene una renta activa.',
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

    # RN-006: No dar de baja con renta activa
    if equipo.tiene_renta_activa():
        messages.error(
            request,
            f'No se puede dar de baja "{equipo.nombre}" porque '
            'tiene una renta activa. Finaliza la renta primero.',
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
    if request.user.es_administrador():
        messages.info(
            request,
            'Como administrador, puedes realizar cambios directamente.',
        )
        return redirect('inventario:lista')

    equipo_pk = request.GET.get('equipo')
    equipo = None
    if equipo_pk:
        equipo = get_object_or_404(Equipo, pk=equipo_pk, activo=True)

    if request.method == 'POST':
        form = SolicitudEquipoForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            comentario = form.cleaned_data['comentario']

            datos_json = {}
            if tipo == 'alta_equipo':
                datos_json = {
                    'nombre': form.cleaned_data.get(
                        'nombre_equipo', ''
                    ),
                    'categoria': form.cleaned_data.get(
                        'categoria_nombre', 'General'
                    ),
                    'descripcion': form.cleaned_data.get(
                        'descripcion_equipo', ''
                    ),
                    'cantidad_total': form.cleaned_data.get(
                        'cantidad_total', 1
                    ) or 1,
                }

            Solicitud.objects.create(
                tipo=tipo,
                solicitante=request.user,
                equipo=equipo,
                comentario=comentario,
                datos_json=datos_json,
            )
            messages.success(
                request,
                'Solicitud enviada. '
                'El administrador la revisará pronto.',
            )
            return redirect('inventario:lista')
    else:
        form = SolicitudEquipoForm()

    contexto = {
        'form': form,
        'equipo': equipo,
    }
    return render(
        request,
        'inventario/solicitar_cambio.html',
        contexto,
    )
