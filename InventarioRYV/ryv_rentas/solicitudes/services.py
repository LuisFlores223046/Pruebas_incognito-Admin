"""Servicios para ejecutar solicitudes aprobadas por el admin."""
from django.utils import timezone


def ejecutar_solicitud(solicitud):
    """
    Ejecuta la acción correspondiente cuando el Admin aprueba
    una solicitud del Empleado.

    Tipos soportados:
    - alta_equipo: crea un nuevo Equipo
    - edicion_equipo: edita campos del Equipo
    - baja_equipo: desactiva el Equipo (si no tiene renta activa)
    - nueva_renta: crea una nueva Renta con uno o más equipos
    - cierre_renta: finaliza la Renta y libera unidades
    """
    from inventario.models import Equipo
    from rentas.models import Renta, Cliente, RentaEquipo

    datos = solicitud.datos_json or {}

    if solicitud.tipo == 'alta_equipo':
        Equipo.objects.create(
            nombre=datos['nombre'],
            descripcion=datos.get('descripcion', ''),
            cantidad_total=datos.get('cantidad_total', 1),
        )

    elif solicitud.tipo == 'edicion_equipo':
        equipo = solicitud.equipo
        campos_permitidos = {
            'nombre', 'descripcion',
            'cantidad_total', 'cantidad_en_mantenimiento',
        }
        if equipo:
            for campo, valor in datos.items():
                if campo in campos_permitidos:
                    setattr(equipo, campo, valor)
            equipo.save()

    elif solicitud.tipo == 'baja_equipo':
        equipo = solicitud.equipo
        if equipo:
            if equipo.tiene_renta_activa():
                raise ValueError(
                    f'El equipo "{equipo.nombre}" tiene '
                    f'{equipo.cantidad_en_renta} unidad(es) en renta '
                    'y no puede darse de baja.'
                )
            cantidad_baja = int(datos.get('cantidad_baja', equipo.cantidad_total))
            if cantidad_baja >= equipo.cantidad_total:
                equipo.activo = False
                equipo.save()
            else:
                equipo.cantidad_total -= cantidad_baja
                equipo.save()

    elif solicitud.tipo == 'nueva_renta':
        cliente, _ = Cliente.objects.get_or_create(
            nombre=datos['cliente_nombre'],
            telefono=datos['cliente_telefono'],
            defaults={
                'direccion': datos.get('cliente_direccion', ''),
                'correo': datos.get('cliente_correo', ''),
            },
        )

        # Soporta lista de equipos (nueva solicitud) y equipo único (legado)
        equipos_datos = datos.get('equipos')
        if equipos_datos:
            equipo_items = []
            for item in equipos_datos:
                equipo = Equipo.objects.get(pk=item['equipo_id'])
                cantidad = int(item['cantidad'])
                if not equipo.tiene_disponibles(cantidad):
                    raise ValueError(
                        f'No hay suficientes unidades disponibles '
                        f'de "{equipo.nombre}".'
                    )
                equipo_items.append((equipo, cantidad))
        else:
            # Legado: solicitud con equipo único
            equipo = solicitud.equipo
            cantidad = int(datos.get('cantidad', 1))
            if not equipo or not equipo.tiene_disponibles(cantidad):
                raise ValueError(
                    f'No hay suficientes unidades disponibles.'
                )
            equipo_items = [(equipo, cantidad)]

        primer_equipo, primer_cantidad = equipo_items[0]
        renta = Renta.objects.create(
            equipo=primer_equipo,
            cliente=cliente,
            registrada_por=solicitud.solicitante,
            cantidad=primer_cantidad,
            fecha_inicio=datos['fecha_inicio'],
            fecha_vencimiento=datos['fecha_vencimiento'],
            precio=datos['precio'],
            deposito=datos.get('deposito', 0),
            metodo_pago=datos.get('metodo_pago', ''),
            notas=datos.get('notas', ''),
        )

        for equipo, cantidad in equipo_items:
            RentaEquipo.objects.create(
                renta=renta, equipo=equipo, cantidad=cantidad
            )
            equipo.cantidad_en_renta += cantidad
            equipo.save()

    elif solicitud.tipo == 'cierre_renta':
        renta = solicitud.renta
        if renta:
            from datetime import date
            renta.estado = 'finalizada'
            renta.fecha_devolucion = date.today()
            renta.save()
            # Liberar unidades (soporta multi-equipo)
            items = renta.items.select_related('equipo').all()
            if items:
                for item in items:
                    item.equipo.cantidad_en_renta = max(
                        0, item.equipo.cantidad_en_renta - item.cantidad
                    )
                    item.equipo.save()
            else:
                equipo = renta.equipo
                equipo.cantidad_en_renta = max(
                    0, equipo.cantidad_en_renta - renta.cantidad
                )
                equipo.save()

    solicitud.estado = 'aprobada'
    solicitud.fecha_resolucion = timezone.now()
    solicitud.save()
