
from flask import render_template, redirect, url_for, jsonify
from flask_login import current_user, login_required
from . import main_bp
import os
import sys

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/inicio_sistema.html')

@main_bp.route('/dashboard')
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.role_selection'))
    
    # Redirigir según el rol del usuario
    if current_user.rol == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.rol == 'docente':
        return redirect(url_for('docente.dashboard'))
    elif current_user.rol == 'alumno':
        return redirect(url_for('alumno.dashboard'))
    
    return redirect(url_for('auth.role_selection'))

@main_bp.route('/shutdown', methods=['POST'])
@login_required
def shutdown():
    """Ruta para cerrar el servidor (solo para administradores)"""
    if current_user.rol != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    # Cerrar el servidor de forma elegante
    func = os.environ.get('WERKZEUG_SERVER_SHUTDOWN')
    if func is None:
        # Para servidores WSGI como Waitress, usar os._exit
        import threading
        def shutdown_server():
            import time
            time.sleep(1)  # Dar tiempo para enviar la respuesta
            os._exit(0)
        
        threading.Thread(target=shutdown_server, daemon=True).start()
        return jsonify({'message': 'Servidor cerrándose...'}), 200
    
    func()
    return jsonify({'message': 'Servidor cerrado'}), 200