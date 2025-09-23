from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario
from . import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        dni = request.form.get('dni')
        password = request.form.get('password')
        
        if not dni or not password:
            flash('Por favor completa todos los campos.', 'error')
            return render_template('auth/login.html')
        
        user = Usuario.query.filter_by(dni=dni, activo=True).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('DNI o contraseña incorrectos.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        dni = request.form.get('dni')
        password = request.form.get('password')
        
        if not dni or not password:
            flash('Por favor completa todos los campos.', 'error')
            return render_template('auth/login_admin.html')
        
        user = Usuario.query.filter_by(dni=dni, activo=True, rol='admin').first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
        else:
            flash('Credenciales incorrectas o no tienes permisos de administrador.', 'error')
    
    return render_template('auth/login_admin.html')

@auth_bp.route('/login/docente', methods=['GET', 'POST'])
def login_docente():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        dni = request.form.get('dni')
        password = request.form.get('password')
        
        if not dni or not password:
            flash('Por favor completa todos los campos.', 'error')
            return render_template('auth/login_docente.html')
        
        user = Usuario.query.filter_by(dni=dni, activo=True, rol='docente').first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('docente.dashboard'))
        else:
            flash('Credenciales incorrectas o no tienes permisos de docente.', 'error')
    
    return render_template('auth/login_docente.html')

@auth_bp.route('/login/alumno', methods=['GET', 'POST'])
def login_alumno():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        dni = request.form.get('dni')
        password = request.form.get('password')
        
        if not dni or not password:
            flash('Por favor completa todos los campos.', 'error')
            return render_template('auth/login_alumno.html')
        
        user = Usuario.query.filter_by(dni=dni, activo=True, rol='alumno').first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('alumno.dashboard'))
        else:
            flash('Credenciales incorrectas o no tienes permisos de estudiante.', 'error')
    
    return render_template('auth/login_alumno.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))

# Ruta de registro removida - Solo el administrador puede registrar usuarios
# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     # Esta funcionalidad ahora está disponible solo para administradores
#     # en el módulo de administración
#     pass
