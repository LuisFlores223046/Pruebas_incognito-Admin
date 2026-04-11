"""
Archivo: generators.py
Descripción: Generadores de reportes PDF para el módulo de reportes del sistema RYV Rentas.
             Implementa la generación de reportes de inventario y rentas por periodo
             usando la librería ReportLab, según lo definido en RF-21, RF-22, RF-24
             y RN-012 del SRS.
Fecha: 2026-04-07
Versión: 1.0
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet
import io
from datetime import date


def generar_pdf_inventario(equipos_qs):
    """
    Genera el reporte PDF con el estado actual del inventario de equipos.

    Construye una tabla con el nombre, cantidad total, unidades en renta,
    en mantenimiento y disponibles de cada equipo activo registrado en el
    sistema, según lo definido en RF-21 y CU-23 del SRS.

    Parámetros:
        equipos_qs (QuerySet): QuerySet de instancias de Equipo activos
        a incluir en el reporte.

    Retorna:
        bytes: Contenido del archivo PDF generado en memoria.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(
        Paragraph(
            'RYV Rentas — Reporte de Inventario',
            styles['Title'],
        )
    )
    elementos.append(
        Paragraph(
            f'Generado el: {date.today()}',
            styles['Normal'],
        )
    )
    elementos.append(Spacer(1, 20))

    datos = [['Equipo', 'Total', 'En Renta', 'Mantenimiento', 'Disponible']]
    for equipo in equipos_qs:
        datos.append([
            equipo.nombre,
            str(equipo.cantidad_total),
            str(equipo.cantidad_en_renta),
            str(equipo.cantidad_en_mantenimiento),
            str(equipo.cantidad_disponible),
        ])

    tabla = Table(datos, colWidths=[190, 60, 70, 90, 80])
    tabla.setStyle(TableStyle([
        (
            'BACKGROUND',
            (0, 0), (-1, 0),
            colors.HexColor('#2C3E50'),
        ),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        (
            'ROWBACKGROUNDS',
            (0, 1), (-1, -1),
            [colors.white, colors.HexColor('#F2F3F4')],
        ),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabla)
    doc.build(elementos)
    return buffer.getvalue()


def generar_pdf_rentas(rentas_qs, periodo_inicio=None, periodo_fin=None):
    """
    Genera el reporte PDF de rentas dentro de un periodo seleccionado.

    Construye una tabla con el equipo, cliente, fechas, precio, depósito,
    monto recibido, cargo por daños y cambio entregado de cada renta,
    incluyendo una fila de totales al final, cumpliendo con RF-22, RF-24
    y RN-012 del SRS.

    Parámetros:
        rentas_qs (QuerySet): QuerySet de instancias de Renta a incluir
        en el reporte.
        periodo_inicio (date): Fecha de inicio del periodo cubierto por
        el reporte. Campo opcional.
        periodo_fin (date): Fecha de fin del periodo cubierto por el reporte.
        Campo opcional.

    Retorna:
        bytes: Contenido del archivo PDF generado en memoria.
    """ 
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elementos = []

    titulo = 'RYV Rentas — Reporte de Rentas por Periodo'
    elementos.append(Paragraph(titulo, styles['Title']))

    if periodo_inicio and periodo_fin:
        elementos.append(
            Paragraph(
                f'Periodo: {periodo_inicio} al {periodo_fin}',
                styles['Normal'],
            )
        )
    elementos.append(
        Paragraph(f'Generado el: {date.today()}', styles['Normal'])
    )
    elementos.append(Spacer(1, 20))

    METODOS = {
        'efectivo': 'Efectivo',
        'transferencia': 'Transfer.',
        'tarjeta': 'Tarjeta',
        'otro': 'Otro',
        '': '—',
    }

    CONDICIONES = {
        'bueno': 'Bueno',
        'daños_menores': 'Daños',
        'inservible': 'Inservible',
        '': '—',
    }

    datos = [
        ['Equipo', 'Cant.', 'Cliente', 'Inicio', 'Vencim.', 'Precio', 'Depósito', 'Recibido', 'Daños', 'Cambio']
    ]
    total_precio = 0
    total_recibido = 0
    total_daños = 0
    for renta in rentas_qs:
        recibido = f'${renta.monto_recibido:,.2f}' if renta.monto_recibido is not None else '—'
        daños_str = f'${renta.cargo_daños:,.2f}' if renta.cargo_daños else '—'
        cambio = ''
        if renta.cambio_entregado is not None:
            cambio = f'${renta.cambio_entregado:,.2f}'
        elif renta.deposito > renta.precio:
            sobrante = renta.deposito - renta.precio
            cambio = f'${sobrante:,.2f}*'
        datos.append([
            renta.equipo.nombre,
            str(renta.cantidad),
            renta.cliente.nombre,
            str(renta.fecha_inicio),
            str(renta.fecha_vencimiento),
            f'${renta.precio:,.2f}',
            f'${renta.deposito:,.2f}',
            recibido,
            daños_str,
            cambio,
        ])
        total_precio += renta.precio
        if renta.monto_recibido is not None:
            total_recibido += renta.monto_recibido
        if renta.cargo_daños:
            total_daños += renta.cargo_daños

    total_row = ['', '', '', '', 'TOTAL', f'${total_precio:,.2f}', '', f'${total_recibido:,.2f}', f'${total_daños:,.2f}' if total_daños else '—', '']
    datos.append(total_row)

    tabla = Table(datos, colWidths=[90, 28, 80, 50, 50, 55, 55, 48, 55, 45])
    tabla.setStyle(TableStyle([
        (
            'BACKGROUND',
            (0, 0), (-1, 0),
            colors.HexColor('#2C3E50'),
        ),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        (
            'ROWBACKGROUNDS',
            (0, 1), (-1, -2),
            [colors.white, colors.HexColor('#F2F3F4')],
        ),
        (
            'BACKGROUND',
            (0, -1), (-1, -1),
            colors.HexColor('#2C3E50'),
        ),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabla)
    elementos.append(Spacer(1, 10))
    elementos.append(
        Paragraph('* Cambio a devolver al cliente (depósito mayor al precio total).', styles['Normal'])
    )
    doc.build(elementos)
    return buffer.getvalue()
