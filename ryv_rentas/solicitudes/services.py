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
    - nueva_renta: crea una nueva Renta y actualiza contador
    - cierre_renta: finaliza la Renta y libera unidades
    """
    from inventario.models import Equipo
    from rentas.models import Renta, Cliente

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
            if not equipo.tiene_renta_activa():
                equipo.activo = False
                equipo.save()
            else:
                raise ValueError(
                    f'El equipo "{equipo.nombre}" tiene '
                    f'{equipo.cantidad_en_renta} unidad(es) en renta '
                    'y no puede darse de baja.'
                )

    elif solicitud.tipo == 'nueva_renta':
        cliente, _ = Cliente.objects.get_or_create(
            nombre=datos['cliente_nombre'],
            telefono=datos['cliente_telefono'],
            defaults={
                'direccion': datos.get('cliente_direccion', ''),
                'correo': datos.get('cliente_correo', ''),
            },
        )
        equipo = solicitud.equipo
        cantidad = int(datos.get('cantidad', 1))
        if equipo:
            if not equipo.tiene_disponibles(cantidad):
                raise ValueError(
                    f'No hay suficientes unidades disponibles '
                    f'de "{equipo.nombre}".'
                )
            Renta.objects.create(
                equipo=equipo,
                cliente=cliente,
                registrada_por=solicitud.solicitante,
                cantidad=cantidad,
                fecha_inicio=datos['fecha_inicio'],
                fecha_vencimiento=datos['fecha_vencimiento'],
                precio=datos['precio'],
                deposito=datos.get('deposito', 0),
                notas=datos.get('notas', ''),
            )
            # RN-002: actualizar contador de renta
            equipo.cantidad_en_renta += cantidad
            equipo.save()

    elif solicitud.tipo == 'cierre_renta':
        renta = solicitud.renta
        if renta:
            from datetime import date
            renta.estado = 'finalizada'
            renta.fecha_devolucion = date.today()
            renta.save()
            # RN-003: liberar unidades
            equipo = renta.equipo
            equipo.cantidad_en_renta = max(
                0, equipo.cantidad_en_renta - renta.cantidad
            )
            equipo.save()

    solicitud.estado = 'aprobada'
    solicitud.fecha_resolucion = timezone.now()
    solicitud.save()
