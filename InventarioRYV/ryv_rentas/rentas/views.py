"""Vistas para el módulo de rentas."""
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import date
from .models import Renta, Cliente, RentaEquipo
from .forms import RentaForm, SolicitudRentaForm, FinalizarRentaForm, equipos_con_disponibles
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


def _parsear_equipos_post(post_data):
    """
    Lee equipo_0/cantidad_0, equipo_1/cantidad_1 … del POST.
    Retorna lista de (equipo_pk_str, cantidad_int) o [] si no hay nada.
    """
    items = []
    i = 0
    while True:
        pk_str = post_data.get(f'equipo_{i}')
        if pk_str is None:
            break
        cantidad_str = post_data.get(f'cantidad_{i}', '1')
        try:
            cantidad = max(1, int(cantidad_str))
        except (ValueError, TypeError):
            cantidad = 1
        items.append((pk_str, cantidad))
        i += 1
    return items


@admin_required
def nueva_renta(request):
    """Crea una nueva renta directamente (solo admin)."""
    equipo_pk = request.GET.get('equipo')
    equipos_qs = equipos_con_disponibles()

    if request.method == 'POST':
        form = RentaForm(request.POST)

        # Parsear filas de equipos del POST
        filas_raw = _parsear_equipos_post(request.POST)
        equipo_items = []
        errores_equipos = []

        if not filas_raw:
            errores_equipos.append('Debes seleccionar al menos un equipo.')
        else:
            equipos_vistos = {}  # pk → cantidad acumulada (para detectar duplicados)
            for pk_str, cantidad in filas_raw:
                try:
                    equipo = Equipo.objects.get(pk=pk_str, activo=True)
                except Equipo.DoesNotExist:
                    errores_equipos.append(f'Equipo con ID {pk_str} no válido.')
                    continue
                # Acumular si el mismo equipo aparece varias veces
                if equipo.pk in equipos_vistos:
                    equipos_vistos[equipo.pk] = (equipo, equipos_vistos[equipo.pk][1] + cantidad)
                else:
                    equipos_vistos[equipo.pk] = (equipo, cantidad)

            for equipo, cantidad in equipos_vistos.values():
                if not equipo.tiene_disponibles(cantidad):
                    errores_equipos.append(
                        f'Solo hay {equipo.cantidad_disponible} unidad(es) '
                        f'disponible(s) de "{equipo.nombre}".'
                    )
                else:
                    equipo_items.append((equipo, cantidad))

        if errores_equipos or not equipo_items:
            for err in errores_equipos:
                messages.error(request, err)
            # Mantener los valores seleccionados para re-render
            return render(request, 'rentas/nueva.html', {
                'form': form,
                'equipos_disponibles': equipos_qs,
                'equipo_inicial_pk': equipo_pk,
            })

        if form.is_valid():
            try:
                cliente, _ = Cliente.objects.get_or_create(
                    nombre=form.cleaned_data['cliente_nombre'],
                    telefono=form.cleaned_data['cliente_telefono'],
                    defaults={
                        'direccion': form.cleaned_data.get('cliente_direccion', ''),
                        'correo': form.cleaned_data.get('cliente_correo', ''),
                    },
                )

                primer_equipo, primer_cantidad = equipo_items[0]
                renta = Renta.objects.create(
                    equipo=primer_equipo,
                    cliente=cliente,
                    registrada_por=request.user,
                    cantidad=primer_cantidad,
                    fecha_inicio=form.cleaned_data['fecha_inicio'],
                    fecha_vencimiento=form.cleaned_data['fecha_vencimiento'],
                    precio=form.cleaned_data['precio'],
                    deposito=form.cleaned_data.get('deposito') or 0,
                    metodo_pago=form.cleaned_data.get('metodo_pago', ''),
                    notas=form.cleaned_data.get('notas', ''),
                )

                # Crear RentaEquipo y actualizar contadores
                for equipo, cantidad in equipo_items:
                    RentaEquipo.objects.create(
                        renta=renta, equipo=equipo, cantidad=cantidad
                    )
                    equipo.cantidad_en_renta += cantidad
                    equipo.save()

                nombres = ', '.join(
                    f'{cantidad}x "{eq.nombre}"'
                    for eq, cantidad in equipo_items
                )
                messages.success(
                    request,
                    f'Renta registrada: {nombres} para {cliente.nombre}.',
                )
                return redirect('rentas:lista')

            except Exception:
                messages.error(
                    request,
                    'Ocurrió un error al crear la renta. Intenta de nuevo.',
                )
    else:
        form = RentaForm()

    return render(request, 'rentas/nueva.html', {
        'form': form,
        'equipos_disponibles': equipos_qs,
        'equipo_inicial_pk': equipo_pk,
    })


@admin_required
def finalizar_renta(request, pk):
    """Finaliza una renta y libera las unidades del equipo (admin). RN-003."""
    renta = get_object_or_404(Renta, pk=pk, estado='activa')

    if request.method == 'POST':
        form = FinalizarRentaForm(request.POST)
        if form.is_valid():
            try:
                monto_recibido = form.cleaned_data.get('monto_recibido')
                cargo_daños = form.cleaned_data.get('cargo_daños') or Decimal('0')

                # Cálculo neto: precio - depósito + daños
                neto = renta.precio - renta.deposito + cargo_daños

                # Validar que si hay saldo pendiente el cliente haya pagado
                if neto > 0:
                    if monto_recibido is None:
                        form.add_error(
                            'monto_recibido',
                            f'El cliente debe pagar ${neto:.2f}. '
                            'Ingresa el monto recibido.',
                        )
                    elif monto_recibido < neto:
                        form.add_error(
                            'monto_recibido',
                            f'El monto recibido (${monto_recibido:.2f}) '
                            f'no cubre el saldo pendiente (${neto:.2f}). '
                            f'Faltan ${neto - monto_recibido:.2f}.',
                        )
                    if not form.cleaned_data.get('metodo_pago_cierre'):
                        form.add_error(
                            'metodo_pago_cierre',
                            'Selecciona el método de pago al cierre.',
                        )

                if form.errors:
                    contexto = {
                        'renta': renta,
                        'hoy': date.today(),
                        'form_finalizar': form,
                    }
                    return render(request, 'rentas/detalle.html', contexto)

                renta.estado = 'finalizada'
                renta.fecha_devolucion = date.today()
                renta.metodo_pago_cierre = form.cleaned_data.get('metodo_pago_cierre', '')
                renta.condicion_devolucion = form.cleaned_data.get('condicion_devolucion', '')
                renta.cargo_daños = cargo_daños if cargo_daños > 0 else None

                if neto <= 0:
                    renta.monto_recibido = Decimal('0')
                    renta.cambio_entregado = abs(neto)
                else:
                    renta.monto_recibido = monto_recibido
                    renta.cambio_entregado = monto_recibido - neto

                notas_dev = form.cleaned_data.get('notas_devolucion', '')
                if notas_dev:
                    separador = '\n' if renta.notas else ''
                    renta.notas = renta.notas + separador + '[Devolución] ' + notas_dev

                renta.save()

                # RN-003: liberar unidades (soporta multi-equipo)
                items = renta.items.select_related('equipo').all()
                if items:
                    for item in items:
                        item.equipo.cantidad_en_renta = max(
                            0, item.equipo.cantidad_en_renta - item.cantidad
                        )
                        item.equipo.save()
                    nombres = ', '.join(
                        f'{i.cantidad}x "{i.equipo.nombre}"' for i in items
                    )
                else:
                    equipo = renta.equipo
                    equipo.cantidad_en_renta = max(
                        0, equipo.cantidad_en_renta - renta.cantidad
                    )
                    equipo.save()
                    nombres = f'{renta.cantidad}x "{equipo.nombre}"'

                messages.success(
                    request,
                    f'Renta finalizada. {nombres} liberado(s).',
                )
                return redirect('historial:detalle', pk=renta.pk)

            except Exception:
                messages.error(
                    request,
                    'Error al finalizar la renta. Intenta de nuevo.',
                )
        else:
            # Errores de validación del form (ej. cargo_daños faltante)
            contexto = {
                'renta': renta,
                'hoy': date.today(),
                'form_finalizar': form,
            }
            return render(request, 'rentas/detalle.html', contexto)

    return redirect('rentas:detalle', pk=pk)


@empleado_o_admin
def solicitar_renta(request):
    """El empleado solicita una nueva renta (RN-008)."""
    if request.user.es_administrador():
        return redirect('rentas:nueva')

    equipos_qs = equipos_con_disponibles()
    equipo_pk = request.GET.get('equipo')

    if request.method == 'POST':
        form = SolicitudRentaForm(request.POST)

        # Parsear filas de equipos del POST
        filas_raw = _parsear_equipos_post(request.POST)
        equipo_items = []
        errores_equipos = []

        if not filas_raw:
            errores_equipos.append('Debes seleccionar al menos un equipo.')
        else:
            equipos_vistos = {}
            for pk_str, cantidad in filas_raw:
                try:
                    equipo = Equipo.objects.get(pk=pk_str, activo=True)
                except Equipo.DoesNotExist:
                    errores_equipos.append(f'Equipo con ID {pk_str} no válido.')
                    continue
                if equipo.pk in equipos_vistos:
                    equipos_vistos[equipo.pk] = (equipo, equipos_vistos[equipo.pk][1] + cantidad)
                else:
                    equipos_vistos[equipo.pk] = (equipo, cantidad)

            for equipo, cantidad in equipos_vistos.values():
                if not equipo.tiene_disponibles(cantidad):
                    errores_equipos.append(
                        f'Solo hay {equipo.cantidad_disponible} unidad(es) '
                        f'disponible(s) de "{equipo.nombre}".'
                    )
                else:
                    equipo_items.append((equipo, cantidad))

        if errores_equipos or not equipo_items:
            for err in errores_equipos:
                messages.error(request, err)
            return render(request, 'rentas/solicitar.html', {
                'form': form,
                'equipos_disponibles': equipos_qs,
                'equipo_inicial_pk': equipo_pk,
            })

        if form.is_valid():
            primer_equipo = equipo_items[0][0]
            datos_json = {
                'equipos': [
                    {'equipo_id': eq.pk, 'cantidad': cant}
                    for eq, cant in equipo_items
                ],
                'cliente_nombre': form.cleaned_data['cliente_nombre'],
                'cliente_telefono': form.cleaned_data['cliente_telefono'],
                'cliente_direccion': form.cleaned_data.get('cliente_direccion', ''),
                'cliente_correo': form.cleaned_data.get('cliente_correo', ''),
                'fecha_inicio': str(form.cleaned_data['fecha_inicio']),
                'fecha_vencimiento': str(form.cleaned_data['fecha_vencimiento']),
                'precio': str(form.cleaned_data['precio']),
                'deposito': str(form.cleaned_data.get('deposito') or 0),
                'metodo_pago': form.cleaned_data.get('metodo_pago', ''),
                'notas': form.cleaned_data.get('notas', ''),
            }

            Solicitud.objects.create(
                tipo='nueva_renta',
                solicitante=request.user,
                equipo=primer_equipo,
                comentario=form.cleaned_data['comentario'],
                datos_json=datos_json,
            )
            messages.success(
                request,
                'Solicitud de renta enviada al administrador.',
            )
            return redirect('rentas:lista')
    else:
        form = SolicitudRentaForm()

    return render(request, 'rentas/solicitar.html', {
        'form': form,
        'equipos_disponibles': equipos_qs,
        'equipo_inicial_pk': equipo_pk,
    })


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
