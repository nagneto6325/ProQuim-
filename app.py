# archivo principal del servidor
# define las rutas y controla que usuario puede ver cada pagina

from flask import Flask, redirect, url_for, session, render_template, jsonify
from functools import wraps
from database.db import init_db

app = Flask(__name__)
app.secret_key = "proquim_secret_key_2026"

# crea la base de datos si no existe
init_db()

# diccionario que define que puede hacer cada rol
# cada rol tiene un conjunto de modulos permitidos
PERMISOS = {
    'Administrador':             {'recetas', 'ordenes', 'inventario', 'reportes', 'configuracion'},
    'Jefe de Produccion':        {'recetas', 'ordenes', 'reportes'},
    'Operario':                  {'ordenes'},
    'Gerente':                   {'reportes'},
    'Responsable de Inventario': {'inventario', 'reportes'},
}

# decora una funcion para que requiera login
def login_requerido(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper

# decora una funcion para que requiera ciertos modulos
# si el rol no tiene permiso, muestra error 403
def requiere_rol(*modulos):
    def decorator(f):
        @wraps(f)
        @login_requerido
        def wrapper(*args, **kwargs):
            rol = session.get('rol', '')
            permisos_rol = PERMISOS.get(rol, set())
            if not any(m in permisos_rol for m in modulos):
                return render_template('error.html',
                    mensaje=f"Acceso denegado: el rol '{rol}' no tiene permiso para esta seccion."), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

# importar los controladores (blueprints)
from controllers.auth_controller import auth_bp
from controllers.recetas_controller import recetas_bp
from controllers.ordenes_controller import ordenes_bp
from controllers.inventario_controller import inventario_bp
from controllers.trazabilidad_controller import trazabilidad_bp
from controllers.reportes_controller import reportes_bp

# funcion para proteger un blueprint completo
# se ejecuta antes de cada request del blueprint
def proteger_blueprint(bp, *modulos):
    @bp.before_request
    def verificar():
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        if modulos:
            rol = session.get('rol', '')
            permisos_rol = PERMISOS.get(rol, set())
            if not any(m in permisos_rol for m in modulos):
                return render_template('error.html',
                    mensaje=f"Acceso denegado: el rol '{rol}' no tiene permiso para esta seccion."), 403

# aplicar proteccion a cada blueprint
proteger_blueprint(recetas_bp,      'recetas')
proteger_blueprint(ordenes_bp,      'ordenes')
proteger_blueprint(inventario_bp,   'inventario')
proteger_blueprint(trazabilidad_bp, 'reportes')
proteger_blueprint(reportes_bp,     'reportes')

# registrar los blueprints en la app
app.register_blueprint(auth_bp)
app.register_blueprint(recetas_bp)
app.register_blueprint(ordenes_bp)
app.register_blueprint(inventario_bp)
app.register_blueprint(trazabilidad_bp)
app.register_blueprint(reportes_bp)

# redirige al login por defecto
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

# panel principal despues de login
@app.route('/dashboard')
@login_requerido
def dashboard():
    from services.receta_service import RecetaService
    from services.inventario_service import InventarioService
    from services.orden_produccion_service import OrdenProduccionService
    recetas    = RecetaService().get_all()
    ordenes    = OrdenProduccionService.get_all()
    inventario = InventarioService.get_all()
    return render_template('dashboard.html',
        user=session.get('user'),
        rol=session.get('rol'),
        total_recetas=len(recetas),
        ordenes_activas=len([o for o in ordenes if o['estado'] == 'Pendiente']),
        alertas_stock=len([i for i in inventario if i['cantidad'] < i['stock_minimo']])
    )

# pagina de configuracion, solo admin puede ver
@app.route('/configuracion')
@requiere_rol('configuracion')
def configuracion_page():
    from services.auth_service import AuthService
    return render_template('configuracion.html',
        usuarios=AuthService.get_usuarios(),
        rol=session.get('rol')
    )

# api para la grafica de produccion por mes
@app.route('/api/produccion_mensual')
@login_requerido
def api_produccion_mensual():
    from services.orden_produccion_service import OrdenProduccionService
    ordenes = OrdenProduccionService.get_all()
    meses = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
    cant = [0]*12
    for o in ordenes:
        if o['estado'] == 'Completada' and o.get('fecha'):
            try:
                m = int(str(o['fecha']).split('-')[1]) - 1
                if 0 <= m < 12:
                    cant[m] += 1
            except Exception:
                pass
    return jsonify({'meses': meses, 'cantidades': cant})

# api para la grafica de distribucion por categoria
@app.route('/api/distribucion_categoria')
@login_requerido
def api_distribucion_categoria():
    from services.receta_service import RecetaService
    cats = {}
    for r in RecetaService().get_all():
        cats[r['categoria']] = cats.get(r['categoria'], 0) + 1
    return jsonify({'categorias': list(cats.keys()), 'cantidades': list(cats.values())})

# api para la grafica de estado de ordenes
@app.route('/api/estado_ordenes')
@login_requerido
def api_estado_ordenes():
    from services.orden_produccion_service import OrdenProduccionService
    est = {}
    for o in OrdenProduccionService.get_all():
        est[o['estado']] = est.get(o['estado'], 0) + 1
    return jsonify({'estados': list(est.keys()), 'cantidades': list(est.values())})

# api para la grafica de consumo de materias primas
@app.route('/api/consumo_materias')
@login_requerido
def api_consumo_materias():
    from repositories.orden_repository import OrdenRepository
    from repositories.quimico_repository import QuimicoRepository
    from services.orden_produccion_service import OrdenProduccionService
    cons = {q['nombre']: 0 for q in QuimicoRepository.get_all()}
    for o in OrdenProduccionService.get_all():
        if o['estado'] == 'Completada':
            for c in OrdenRepository.get_consumos_by_orden(o['id']):
                cons[c['quimico_nombre']] = cons.get(c['quimico_nombre'], 0) + c['cantidad_consumida']
    return jsonify({'materiales': list(cons.keys()), 'consumos': list(cons.values())})

# arranca el servidor
if __name__ == '__main__':
    print("\n=== PROQUIM ===\nhttp://127.0.0.1:5000")
    print("  admin/admin123 · jefe/jefe123 · operario/operario123\n")
    app.run(debug=True, use_reloader=False, port=5000)