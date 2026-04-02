"""Vistas para el módulo de rentas."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import date
from .models import Renta, Cliente
from .forms import RentaForm, SolicitudRentaForm, FinalizarRentaForm
from inventario.models import Equipo
from authentication.decorators import admin_required, empleado_o_admin
from solicitudes.models import Solicitud


@empleado_o_admin
def rentas_activas(request):
    """Lista rentas activas con filtros por cliente y equipo."""
    rentas = Renta.objects.filter(
        estado='activa'
    ).select_related('equipo', 'cliente', 'registrada_por')

    cliente_nombre = request.GET.get('cliente', '').strip()
    equipo_nombre = request.GET.get('equipo', '').strip()

    if cliente_nombre:
        rentas = rentas.filter(
            cliente__nombre__icontains=cliente_nombre
        )
    if equipo_nombre:
        rentas = rentas.filter(
            equipo__nombre__icontains=equipo_nombre
        )

    # Ordenar por vencimiento más próximo primero
    rentas = rentas.order_by('fecha_vencimiento')

    paginator = Paginator(rentas, 20)
    page = request.GET.get('page', 1)
    rentas_page = paginator.get_page(page)

    contexto = {
        'rentas': rentas_page,
        'filtro_cliente': cliente_nombre,
        'filtro_equipo': equipo_nombre,
        'hoy': date.today(),
    }
    return render(request, 'rentas/activas.html', contexto)


@empleado_o_admin
def detalle_renta(request, pk):
    """Muestra el detalle de una renta."""
    renta = get_object_or_404(
        Renta.objects.select_related(
            'equipo', 'cliente', 'registrada_por'
        ),
        pk=pk,
    )
    form_finalizar = None
    if (
        renta.estado == 'activa'
        and request.user.es_administrador()
    ):
        form_finalizar = FinalizarRentaForm()

    contexto = {
        'renta': renta,
        'hoy': date.today(),
        'form_finalizar': form_finalizar,
    }
    return render(request, 'rentas/detalle.html', contexto)


@admin_required
def nueva_renta(request):
    """Crea una nueva renta directamente (solo admin). Respeta RN-001."""
    equipo_pk = request.GET.get('equipo')
    equipo_inicial = None
    if equipo_pk:
        equipo_inicial = get_object_or_404(
            Equipo, pk=equipo_pk, activo=True
        )

    if request.method == 'POST':
        form = RentaForm(request.POST)
        if form.is_valid():
            try:
                equipo = form.cleaned_data['equipo']

                # RN-001: Verificar renta activa única
                if equipo.tiene_renta_activa():
                    messages.error(
                        request,
                        f'El equipo "{equipo.nombre}" ya tiene '
                        'una renta activa.',
                    )
                    return render(
                        request,
                        'rentas/nueva.html',
                        {'form': form},
                    )

                # Obtener o crear cliente (RN-005)
                cliente, _ = Cliente.objects.get_or_create(
                    nombre=form.cleaned_data['cliente_nombre'],
                    telefono=form.cleaned_data['cliente_telefono'],
                    defaults={
                        'direccion': form.cleaned_data.get(
                            'cliente_direccion', ''
                        ),
                        'correo': form.cleaned_data.get(
                            'cliente_correo', ''
                        ),
                    },
                )

                renta = Renta.objects.create(
                    equipo=equipo,
                    cliente=cliente,
                    registrada_por=request.user,
                    fecha_inicio=form.cleaned_data['fecha_inicio'],
                    fecha_vencimiento=(
                        form.cleaned_data['fecha_vencimiento']
                    ),
                    precio=form.cleaned_data['precio'],
                    deposito=form.cleaned_data.get('deposito') or 0,
                    notas=form.cleaned_data.get('notas', ''),
                )

                # RN-002: marcar equipo como rentado
                equipo.estado = 'rentado'
                equipo.save()

                messages.success(
                    request,
                    f'Renta creada para "{cliente.nombre}" — '
                    f'equipo: {equipo.nombre}.',
                )
                return redirect('rentas:detalle', pk=renta.pk)

            except Exception:
                messages.error(
                    request,
                    'Ocurrió un error al crear la renta. '
                    'Intenta de nuevo.',
                )
    else:
        initial = {}
        if equipo_inicial:
            initial['equipo'] = equipo_inicial
        form = RentaForm(initial=initial)

    return render(request, 'rentas/nueva.html', {'form': form})


@admin_required
def finalizar_renta(request, pk):
    """Finaliza una renta y libera el equipo (solo admin). RN-003."""
    renta = get_object_or_404(Renta, pk=pk, estado='activa')

    if request.method == 'POST':
        form = FinalizarRentaForm(request.POST)
        if form.is_valid():
            try:
                renta.estado = 'finalizada'
                renta.fecha_devolucion = date.today()
                notas_dev = form.cleaned_data.get(
                    'notas_devolucion', ''
                )
                if notas_dev:
                    separador = '\n' if renta.notas else ''
                    renta.notas = (
                        renta.notas
                        + separador
                        + '[Devolución] '
                        + notas_dev
                    )
                renta.save()

                # RN-003: liberar equipo
                renta.equipo.estado = 'disponible'
                renta.equipo.save()

                messages.success(
                    request,
                    f'Renta finalizada. Equipo '
                    f'"{renta.equipo.nombre}" marcado disponible.',
                )
                return redirect('historial:detalle', pk=renta.pk)

            except Exception:
                messages.error(
                    request,
                    'Error al finalizar la renta. Intenta de nuevo.',
                )

    return redirect('rentas:detalle', pk=pk)


@empleado_o_admin
def solicitar_renta(request):
    """El empleado solicita una nueva renta (RN-008)."""
    if request.user.es_administrador():
        return redirect('rentas:nueva')

    if request.method == 'POST':
        form = SolicitudRentaForm(request.POST)
        if form.is_valid():
            equipo = form.cleaned_data['equipo']
            datos_json = {
                'cliente_nombre': (
                    form.cleaned_data['cliente_nombre']
                ),
                'cliente_telefono': (
                    form.cleaned_data['cliente_telefono']
                ),
                'cliente_direccion': form.cleaned_data.get(
                    'cliente_direccion', ''
                ),
                'cliente_correo': form.cleaned_data.get(
                    'cliente_correo', ''
                ),
                'fecha_inicio': str(
                    form.cleaned_data['fecha_inicio']
                ),
                'fecha_vencimiento': str(
                    form.cleaned_data['fecha_vencimiento']
                ),
                'precio': str(form.cleaned_data['precio']),
                'deposito': str(
                    form.cleaned_data.get('deposito') or 0
                ),
                'notas': form.cleaned_data.get('notas', ''),
            }

            Solicitud.objects.create(
                tipo='nueva_renta',
                solicitante=request.user,
                equipo=equipo,
                comentario=form.cleaned_data['comentario'],
                datos_json=datos_json,
            )
            messages.success(
                request,
                'Solicitud de renta enviada al administrador.',
            )
            return redirect('rentas:lista')
    else:
        equipo_pk = request.GET.get('equipo')
        initial = {}
        if equipo_pk:
            equipo_obj = get_object_or_404(
                Equipo, pk=equipo_pk, activo=True
            )
            initial['equipo'] = equipo_obj
        form = SolicitudRentaForm(initial=initial)

    return render(request, 'rentas/solicitar.html', {'form': form})


@empleado_o_admin
def solicitar_cierre(request, pk):
    """El empleado solicita el cierre de una renta (RN-008)."""
    if request.user.es_administrador():
        return redirect('rentas:finalizar', pk=pk)

    renta = get_object_or_404(Renta, pk=pk, estado='activa')

    if request.method == 'POST':
        comentario = request.POST.get('comentario', '').strip()
        if not comentario:
            comentario = 'Solicitud de cierre de renta.'

        Solicitud.objects.create(
            tipo='cierre_renta',
            solicitante=request.user,
            renta=renta,
            equipo=renta.equipo,
            comentario=comentario,
        )
        messages.success(
            request,
            'Solicitud de cierre enviada al administrador.',
        )
        return redirect('rentas:detalle', pk=pk)

    contexto = {
        'renta': renta,
        'hoy': date.today(),
        'solicitar_cierre': True,
    }
    return render(request, 'rentas/detalle.html', contexto)
