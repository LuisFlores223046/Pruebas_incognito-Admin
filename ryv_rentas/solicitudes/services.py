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
    - nueva_renta: crea una nueva Renta y actualiza estado del equipo
    - cierre_renta: finaliza la Renta y libera el equipo
    """
    from inventario.models import Equipo, Categoria
    from rentas.models import Renta, Cliente

    datos = solicitud.datos_json or {}

    if solicitud.tipo == 'alta_equipo':
        categoria, _ = Categoria.objects.get_or_create(
            nombre=datos.get('categoria', 'General')
        )
        Equipo.objects.create(
            nombre=datos['nombre'],
            categoria=categoria,
            descripcion=datos.get('descripcion', ''),
            cantidad_total=datos.get('cantidad_total', 1),
            cantidad_disponible=datos.get('cantidad_total', 1),
        )

    elif solicitud.tipo == 'edicion_equipo':
        equipo = solicitud.equipo
        if equipo:
            for campo, valor in datos.items():
                if hasattr(equipo, campo):
                    setattr(equipo, campo, valor)
            equipo.save()

    elif solicitud.tipo == 'baja_equipo':
        equipo = solicitud.equipo
        if equipo:
            # RN-006: no dar de baja con renta activa
            if not equipo.tiene_renta_activa():
                equipo.activo = False
                equipo.save()
            else:
                raise ValueError(
                    f'El equipo "{equipo.nombre}" tiene una renta '
                    'activa y no puede darse de baja.'
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
        if equipo:
            renta = Renta.objects.create(
                equipo=equipo,
                cliente=cliente,
                registrada_por=solicitud.solicitante,
                fecha_inicio=datos['fecha_inicio'],
                fecha_vencimiento=datos['fecha_vencimiento'],
                precio=datos['precio'],
                deposito=datos.get('deposito', 0),
                notas=datos.get('notas', ''),
            )
            # RN-002: marcar equipo como rentado
            equipo.estado = 'rentado'
            equipo.save()

    elif solicitud.tipo == 'cierre_renta':
        renta = solicitud.renta
        if renta:
            from datetime import date
            renta.estado = 'finalizada'
            renta.fecha_devolucion = date.today()
            renta.save()
            # RN-003: liberar equipo
            renta.equipo.estado = 'disponible'
            renta.equipo.save()

    solicitud.estado = 'aprobada'
    solicitud.fecha_resolucion = timezone.now()
    solicitud.save()
