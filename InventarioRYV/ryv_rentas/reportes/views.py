"""Vistas para el módulo de reportes."""
import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import ReporteGenerado
from .forms import ReporteRentasForm
from .generators import generar_pdf_inventario, generar_pdf_rentas
from inventario.models import Equipo
from rentas.models import Renta
from authentication.decorators import admin_required


@admin_required
def panel_reportes(request):
    """Panel principal de generación de reportes (solo admin)."""
    form_rentas = ReporteRentasForm()
    reportes_recientes = ReporteGenerado.objects.select_related(
        'generado_por'
    )[:5]

    contexto = {
        'form_rentas': form_rentas,
        'reportes_recientes': reportes_recientes,
    }
    return render(request, 'reportes/panel.html', contexto)


@admin_required
def generar_inventario(request):
    """Genera y descarga el PDF de inventario actual."""
    if request.method == 'POST':
        try:
            equipos = Equipo.objects.filter(
                activo=True
            ).order_by('nombre')

            pdf_bytes = generar_pdf_inventario(equipos)

            nombre_archivo = (
                'inventario_'
                + datetime.date.today().strftime('%Y%m%d')
                + '.pdf'
            )

            ReporteGenerado.objects.create(
                tipo='inventario',
                generado_por=request.user,
                archivo_nombre=nombre_archivo,
            )

            response = HttpResponse(
                pdf_bytes,
                content_type='application/pdf',
            )
            response['Content-Disposition'] = (
                f'attachment; filename="{nombre_archivo}"'
            )
            return response

        except Exception:
            messages.error(
                request,
                'Error al generar el reporte de inventario.',
            )

    return redirect('reportes:panel')


@admin_required
def generar_rentas(request):
    """Genera y descarga el PDF de rentas por periodo (RN-012)."""
    if request.method == 'POST':
        form = ReporteRentasForm(request.POST)
        if form.is_valid():
            try:
                inicio = form.cleaned_data['periodo_inicio']
                fin = form.cleaned_data['periodo_fin']

                rentas = Renta.objects.filter(
                    fecha_inicio__gte=inicio,
                    fecha_inicio__lte=fin,
                ).select_related(
                    'equipo', 'cliente'
                ).order_by('fecha_inicio')

                pdf_bytes = generar_pdf_rentas(rentas, inicio, fin)

                nombre_archivo = (
                    'rentas_'
                    + inicio.strftime('%Y%m%d')
                    + '_'
                    + fin.strftime('%Y%m%d')
                    + '.pdf'
                )

                ReporteGenerado.objects.create(
                    tipo='rentas',
                    generado_por=request.user,
                    archivo_nombre=nombre_archivo,
                    periodo_inicio=inicio,
                    periodo_fin=fin,
                )

                response = HttpResponse(
                    pdf_bytes,
                    content_type='application/pdf',
                )
                response['Content-Disposition'] = (
                    f'attachment; filename="{nombre_archivo}"'
                )
                return response

            except Exception:
                messages.error(
                    request,
                    'Error al generar el reporte de rentas.',
                )
        else:
            messages.error(request, 'Fechas inválidas.')

    return redirect('reportes:panel')


@admin_required
def descargar_pdf(request, pk):
    """Re-genera y descarga un reporte previamente registrado."""
    reporte = get_object_or_404(ReporteGenerado, pk=pk)

    try:
        if reporte.tipo == 'inventario':
            equipos = Equipo.objects.filter(
                activo=True
            ).order_by('nombre')
            pdf_bytes = generar_pdf_inventario(equipos)
        else:
            rentas = Renta.objects.filter(
                fecha_inicio__gte=reporte.periodo_inicio,
                fecha_inicio__lte=reporte.periodo_fin,
            ).select_related('equipo', 'cliente')
            pdf_bytes = generar_pdf_rentas(
                rentas,
                reporte.periodo_inicio,
                reporte.periodo_fin,
            )

        response = HttpResponse(
            pdf_bytes, content_type='application/pdf'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="{reporte.archivo_nombre}"'
        )
        return response

    except Exception:
        messages.error(
            request,
            'Error al re-generar el reporte.',
        )
        return redirect('reportes:historial')


@admin_required
def historial_reportes(request):
    """Lista el historial de reportes generados."""
    reportes = ReporteGenerado.objects.select_related(
        'generado_por'
    ).order_by('-fecha_generacion')

    return render(
        request,
        'reportes/historial.html',
        {'reportes': reportes},
    )
