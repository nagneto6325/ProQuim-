from flask import Blueprint, render_template, request, jsonify, session
from services.receta_service import RecetaService
from services.inventario_service import InventarioService
from services.validacion_quimica_service import ValidacionQuimicaService

# blueprint para las rutas de recetas
recetas_bp = Blueprint('recetas', __name__)

receta_service = RecetaService()

# pagina principal de recetas
@recetas_bp.route('/recetas')
def recetas_page():
    return render_template('recetas.html',
        recetas=receta_service.get_all(),
        quimicos=InventarioService.get_all()
    )

# guarda una receta nueva en la base de datos
@recetas_bp.route('/crear_receta', methods=['POST'])
def crear_receta():
    # import lazy para evitar ciclos en la inicialización de módulos
    from repositories.quimico_repository import QuimicoRepository

    data = request.get_json()
    ingredientes = data.get('ingredientes', [])

    # Verificar que cada ingrediente exista en el inventario
    faltantes_inventario = []
    for ing in ingredientes:
        quimico = QuimicoRepository.get_by_nombre(ing.get('nombre', ''))
        if not quimico:
            faltantes_inventario.append(ing.get('nombre'))

    if faltantes_inventario:
        return jsonify({
            'success': False,
            'mensaje': (
                f"Los siguientes ingredientes no existen en el inventario: "
                f"{', '.join(faltantes_inventario)}. "
                f"Agrégalos primero desde la sección de Inventario."
            )
        }), 400

    validacion = ValidacionQuimicaService().validar(ingredientes)
    receta_service.create(
        data.get('nombre'), data.get('categoria'),
        data.get('rendimiento', 1000), ingredientes,
        validacion['compatible']
    )
    return jsonify({'success': True, 'mensaje': validacion['mensaje']})

# elimina una receta por ID
# no permite borrar si tiene órdenes asociadas
@recetas_bp.route('/eliminar_receta/<int:receta_id>', methods=['DELETE'])
def eliminar_receta(receta_id):
    # import lazy para evitar ciclos en la inicialización de módulos
    from database.connection import db

    conn = db.get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, nombre FROM recetas WHERE id = ?", (receta_id,))
    receta = cur.fetchone()
    if not receta:
        conn.close()
        return jsonify({'success': False, 'error': 'Receta no encontrada'}), 404

    cur.execute(
        "SELECT COUNT(*) FROM ordenes_produccion WHERE receta_id = ?",
        (receta_id,)
    )
    total_ordenes = cur.fetchone()[0]
    if total_ordenes > 0:
        conn.close()
        return jsonify({
            'success': False,
            'error': f'No se puede eliminar: la receta tiene {total_ordenes} orden(es) asociada(s).'
        }), 409

    cur.execute("DELETE FROM ingredientes WHERE receta_id = ?", (receta_id,))
    cur.execute("DELETE FROM recetas WHERE id = ?", (receta_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'mensaje': 'Receta eliminada correctamente.'})

# valida una receta sin guardarla
@recetas_bp.route('/validar_receta', methods=['POST'])
def validar_receta():
    data = request.get_json()
    v = ValidacionQuimicaService()
    tipo = data.get('tipo', 'basica')
    if tipo == 'gramaje':
        return jsonify(v.validar_gramaje(data.get('ingredientes', []), 1000))
    elif tipo == 'completa':
        return jsonify(v.validar_completa(data.get('ingredientes', []), 1000))
    return jsonify(v.validar(data.get('ingredientes', [])))

# cambia la estrategia de validacion
@recetas_bp.route('/cambiar_validacion', methods=['POST'])
def cambiar_validacion():
    session['estrategia_validacion'] = request.get_json().get('tipo', 'basica')
    return jsonify({"mensaje": "Estrategia cambiada"})