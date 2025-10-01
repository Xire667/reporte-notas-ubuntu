
from flask import render_template, redirect, url_for
from flask_login import current_user
from . import main_bp

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