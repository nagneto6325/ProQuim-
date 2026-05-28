from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from services.auth_service import AuthService

# blueprint para las rutas de autenticacion
auth_bp = Blueprint('auth', __name__)

# pagina de login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # intenta autenticar al usuario
        resultado = AuthService.login(username, password)
        if resultado['success']:
            # guarda los datos en la sesion
            session['user']    = resultado['user']
            session['rol']     = resultado['rol']
            session['user_id'] = resultado['user_id']
            return redirect(url_for('dashboard'))
        else:
            error = resultado['error']

    return render_template('login.html', error=error)

# cierra la sesion
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

# crea un usuario nuevo (solo admin puede llamar esto)
@auth_bp.route('/crear_usuario', methods=['POST'])
def crear_usuario():
    d = request.get_json()
    return jsonify(AuthService.crear_usuario(d.get('username'), d.get('password'), d.get('rol')))