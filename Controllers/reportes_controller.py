from flask import Blueprint, render_template, send_file
from services.reporte_service import ReporteService
import io
import csv

# blueprint para las rutas de reportes
reportes_bp = Blueprint('reportes', __name__)

# pagina principal de reportes
@reportes_bp.route('/reportes')
def reportes_page():
    stats = ReporteService.get_estadisticas()
    return render_template('reportes.html',
        total_ordenes=stats['total_ordenes'],
        ordenes_completadas=stats['ordenes_completadas'],
        eficiencia=stats['eficiencia'],
        ordenes=ReporteService.generar_reporte_produccion()
    )

# exporta los datos a un archivo csv (se puede abrir con excel)
@reportes_bp.route('/exportar_excel')
def exportar_excel():
    ordenes = ReporteService.generar_reporte_produccion()
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(['ID', 'Receta', 'Cantidad', 'Estado', 'Fecha', 'Lote'])
    for o in ordenes:
        w.writerow([o['orden_id'], o['receta_nombre'], o['cantidad'],
                    o['estado'], o['fecha'], o['lote'] or 'N/A'])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        download_name='reporte.csv',
        as_attachment=True
    )

# exporta el reporte a pdf
@reportes_bp.route('/exportar_pdf')
def exportar_pdf():
    pdf_bytes = ReporteService.generar_pdf()
    return send_file(
        io.BytesIO(pdf_bytes),
        download_name='reporte_produccion.pdf',
        as_attachment=True,
        mimetype='application/pdf'
    )