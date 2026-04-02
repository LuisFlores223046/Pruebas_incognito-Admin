"""Generadores de PDF para el módulo de reportes."""
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
    Genera PDF con el estado actual del inventario.

    Args:
        equipos_qs: QuerySet de Equipo activos.

    Returns:
        bytes del PDF generado.
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

    datos = [['Equipo', 'Categoría', 'Estado', 'Disponibles', 'Total']]
    for equipo in equipos_qs:
        datos.append([
            equipo.nombre,
            equipo.categoria.nombre if equipo.categoria else '—',
            equipo.get_estado_display(),
            str(equipo.cantidad_disponible),
            str(equipo.cantidad_total),
        ])

    tabla = Table(datos, colWidths=[180, 120, 90, 80, 60])
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
        ('ALIGN', (3, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabla)
    doc.build(elementos)
    return buffer.getvalue()


def generar_pdf_rentas(rentas_qs, periodo_inicio=None, periodo_fin=None):
    """
    Genera PDF de rentas por periodo con ingreso total (RN-012).

    Args:
        rentas_qs: QuerySet de Renta.
        periodo_inicio: fecha de inicio del periodo (opcional).
        periodo_fin: fecha de fin del periodo (opcional).

    Returns:
        bytes del PDF generado.
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

    datos = [
        ['Equipo', 'Cliente', 'Inicio', 'Vencimiento', 'Precio (MXN)']
    ]
    total = 0
    for renta in rentas_qs:
        datos.append([
            renta.equipo.nombre,
            renta.cliente.nombre,
            str(renta.fecha_inicio),
            str(renta.fecha_vencimiento),
            f'${renta.precio:,.2f}',
        ])
        total += renta.precio

    datos.append(['', '', '', 'TOTAL', f'${total:,.2f}'])

    tabla = Table(datos, colWidths=[150, 130, 80, 90, 90])
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
        ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabla)
    doc.build(elementos)
    return buffer.getvalue()
