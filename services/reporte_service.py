import sys
import os
import io
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.orden_repository import OrdenRepository
from repositories.receta_repository import RecetaRepository
from patrones import ReporteFactory, crear_reporte_con_exportaciones

class ReporteService:
    @staticmethod
    def get_estadisticas():
        ordenes = OrdenRepository.get_all()
        total = len(ordenes)
        completadas = len([o for o in ordenes if o['estado'] == 'Completada'])
        eficiencia = (completadas / total * 100) if total > 0 else 0

        factory = ReporteFactory()
        reporte = factory.crear("produccion", {"ordenes": ordenes})
        datos_reporte = reporte.generar()

        reporte_con_export = crear_reporte_con_exportaciones(datos_reporte, pdf=True, excel=True)
        reporte_final = reporte_con_export.generar()

        return {
            'total_ordenes': total,
            'ordenes_completadas': completadas,
            'ordenes_pendientes': total - completadas,
            'eficiencia': round(eficiencia, 1),
            'reporte_factory': datos_reporte,
            'reporte_decorator': reporte_final
        }

    @staticmethod
    def generar_reporte_produccion():
        ordenes = OrdenRepository.get_all()
        resultado = []
        for orden in ordenes:
            receta = RecetaRepository.get_by_id(orden['receta_id'])
            trazabilidad = OrdenRepository.get_trazabilidad_by_orden(orden['id'])
            resultado.append({
                'orden_id': orden['id'],
                'receta_nombre': receta['nombre'] if receta else 'N/A',
                'cantidad': orden['cantidad_producir'],
                'estado': orden['estado'],
                'fecha': orden['fecha'],
                'lote': trazabilidad['lote_produccion'] if trazabilidad else None
            })
        return resultado

    @staticmethod
    def generar_pdf() -> bytes:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        titulo_style = ParagraphStyle('titulo', parent=styles['Title'],
                                      fontSize=18, textColor=colors.HexColor('#4f46e5'),
                                      alignment=TA_CENTER)
        subtitulo_style = ParagraphStyle('subtitulo', parent=styles['Normal'],
                                         fontSize=11, textColor=colors.HexColor('#64748b'),
                                         alignment=TA_CENTER)
        seccion_style = ParagraphStyle('seccion', parent=styles['Heading2'],
                                       fontSize=13, textColor=colors.HexColor('#4f46e5'),
                                       spaceAfter=6)

        elementos = []

        elementos.append(Paragraph("ProQuim Gestion", titulo_style))
        elementos.append(Paragraph("Reporte de Produccion", subtitulo_style))
        elementos.append(Spacer(1, 0.5*cm))

        stats = ReporteService.get_estadisticas()
        elementos.append(Paragraph("Resumen General", seccion_style))

        datos_resumen = [
            ['Metrica', 'Valor'],
            ['Total de Ordenes',    str(stats['total_ordenes'])],
            ['Ordenes Completadas', str(stats['ordenes_completadas'])],
            ['Ordenes Pendientes',  str(stats['ordenes_pendientes'])],
            ['Eficiencia',          f"{stats['eficiencia']}%"],
        ]

        tabla_resumen = Table(datos_resumen, colWidths=[8*cm, 6*cm])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
            ('TEXTCOLOR',     (0, 0), (-1, 0), colors.white),
            ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, 0), 11),
            ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.HexColor('#f0f4ff'), colors.white]),
            ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('FONTNAME',      (0, 1), (0, -1), 'Helvetica-Bold'),
            ('TOPPADDING',    (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elementos.append(tabla_resumen)
        elementos.append(Spacer(1, 0.6*cm))

        elementos.append(Paragraph("Detalle de Ordenes de Produccion", seccion_style))

        ordenes = ReporteService.generar_reporte_produccion()
        datos_ordenes = [['ID', 'Receta', 'Cantidad (kg)', 'Estado', 'Fecha', 'Lote']]
        for o in ordenes:
            datos_ordenes.append([
                str(o['orden_id']),
                o['receta_nombre'],
                str(o['cantidad']),
                o['estado'],
                str(o['fecha'])[:10],
                o['lote'] or 'Sin lote'
            ])

        tabla_ordenes = Table(datos_ordenes,
                              colWidths=[1.2*cm, 4.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 3.5*cm])
        tabla_ordenes.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR',     (0, 0), (-1, 0), colors.white),
            ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, -1), 9),
            ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white]),
            ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING',    (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        elementos.append(tabla_ordenes)
        elementos.append(Spacer(1, 0.6*cm))

        from datetime import datetime
        elementos.append(Paragraph(
            f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} - ProQuim Gestion",
            ParagraphStyle('pie', parent=styles['Normal'],
                           fontSize=8, textColor=colors.HexColor('#94a3b8'),
                           alignment=TA_CENTER)
        ))

        doc.build(elementos)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes