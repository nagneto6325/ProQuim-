from flask import Blueprint, render_template, request, jsonify, session
from services.orden_produccion_service import OrdenProduccionService
from services.receta_service import RecetaService

# blueprint para las rutas de ordenes de produccion
ordenes_bp = Blueprint('ordenes', __name__)

receta_service = RecetaService()

# pagina principal de ordenes
@ordenes_bp.route('/ordenes')
def ordenes_page():
    return render_template('ordenes_produccion.html',
        ordenes=OrdenProduccionService.get_all(),
        recetas=receta_service.get_all(),
        rol=session.get('rol')
    )

# crear una orden nueva (la guarda en estado pendiente)
@ordenes_bp.route('/crear_orden', methods=['POST'])
def crear_orden():
    data = request.get_json()
    return jsonify(OrdenProduccionService.crear_orden(
        data.get('receta_id'), data.get('cantidad')
    ))

# ejecutar una orden existente (descuenta stock y genera lote)
@ordenes_bp.route('/ejecutar_orden', methods=['POST'])
def ejecutar_orden():
    data = request.get_json()
    orden_id = data.get('orden_id')
    responsable = session.get('user', 'sistema')

    print(f"[DEBUG] Ejecutando orden {orden_id} por {responsable}")
    resultado = OrdenProduccionService.ejecutar_orden(orden_id, responsable)
    print(f"[DEBUG] Resultado: {resultado}")

    return jsonify(resultado)

# endpoint de diagnóstico — muestra el stock actual en consola y en pantalla
# útil para verificar que los cambios se están guardando
@ordenes_bp.route('/debug_inventario')
def debug_inventario():
    from database.connection import db
    conn = db.get_connection()
    cur = conn.cursor()
    items = [dict(r) for r in cur.execute("SELECT id, nombre, cantidad FROM inventario")]
    ordenes = [dict(r) for r in cur.execute("SELECT id, receta_id, cantidad_producir, estado FROM ordenes_produccion")]
    conn.close()
    return jsonify({'inventario': items, 'ordenes': ordenes})