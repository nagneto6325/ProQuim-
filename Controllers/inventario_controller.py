from flask import Blueprint, render_template, request, jsonify
from services.inventario_service import InventarioService

# blueprint para las rutas de inventario
inventario_bp = Blueprint('inventario', __name__)

# pagina principal de inventario
@inventario_bp.route('/inventario')
def inventario_page():
    return render_template('inventario.html', inventario=InventarioService.get_all())

# actualiza la cantidad de un quimico usando su ID real
# puede ser una entrada manual (compra) sumando al stock actual
@inventario_bp.route('/actualizar_stock', methods=['POST'])
def actualizar_stock():
    data = request.get_json()
    quimico_id = data.get('quimico_id')
    cantidad_agregar = data.get('cantidad_agregar', 0)

    if not quimico_id:
        return jsonify({"success": False, "error": "ID de químico requerido"})

    # Obtener stock actual y sumar la entrada
    from repositories.quimico_repository import QuimicoRepository
    item = QuimicoRepository.get_by_id(quimico_id)
    if not item:
        return jsonify({"success": False, "error": "Químico no encontrado"})

    nueva_cantidad = float(item['cantidad']) + float(cantidad_agregar)
    return jsonify(InventarioService.actualizar_stock(quimico_id, nueva_cantidad))