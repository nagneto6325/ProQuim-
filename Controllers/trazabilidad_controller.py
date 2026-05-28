from flask import Blueprint, jsonify
from services.trazabilidad_service import TrazabilidadService

# blueprint para las rutas de trazabilidad
trazabilidad_bp = Blueprint('trazabilidad', __name__)

# endpoint para consultar la trazabilidad completa de una orden
# ejemplo: /trazabilidad/1
@trazabilidad_bp.route('/trazabilidad/<int:orden_id>')
def get_trazabilidad(orden_id):
    # busca toda la informacion de la orden
    resultado = TrazabilidadService.get_trazabilidad_completa(orden_id)
    if not resultado:
        return jsonify({'error': 'Orden no encontrada'}), 404
    return jsonify(resultado)