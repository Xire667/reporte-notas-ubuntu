from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Usuario, Curso, CursoAlumno, CursoDocente, Nota
from . import alumno_bp

def alumno_required(f):
    """Decorator para requerir rol de alumno"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'alumno':
            flash('No tienes permisos para acceder a esta página.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@alumno_bp.route('/')
@login_required
@alumno_required
def dashboard():
    # Obtener cursos del alumno
    cursos = db.session.query(Curso).join(CursoAlumno).filter(
        CursoAlumno.alumno_id == current_user.id
    ).all()
    
    return render_template('alumno/dashboard.html', cursos=cursos)

@alumno_bp.route('/notas')
@login_required
@alumno_required
def ver_notas():
    # Obtener todas las notas del alumno
    notas = db.session.query(Nota, Curso).join(Curso).filter(
        Nota.alumno_id == current_user.id,
        Nota.estado == 'publicada'
    ).all()
    
    return render_template('alumno/notas.html', notas=notas)

@alumno_bp.route('/notas/curso/<int:curso_id>')
@login_required
@alumno_required
def ver_notas_curso(curso_id):
    # Verificar que el alumno esté matriculado en el curso
    matricula = CursoAlumno.query.filter_by(
        curso_id=curso_id, 
        alumno_id=current_user.id
    ).first()
    
    if not matricula:
        flash('No estás matriculado en este curso.', 'error')
        return redirect(url_for('alumno.dashboard'))
    
    # Obtener nota del curso
    nota = Nota.query.filter_by(
        curso_id=curso_id, 
        alumno_id=current_user.id
    ).first()
    
    # Obtener curso con información del docente
    curso = db.session.query(Curso).join(CursoDocente).join(Usuario).filter(
        Curso.id == curso_id,
        Usuario.rol == 'docente'
    ).first()
    
    # Si no se encuentra el curso con docente, obtener solo el curso
    if not curso:
        curso = Curso.query.get(curso_id)
    
    return render_template('alumno/notas_curso.html', 
                         nota=nota, 
                         curso=curso)

@alumno_bp.route('/cursos')
@login_required
@alumno_required
def ver_cursos():
    # Obtener cursos del alumno con información de notas
    cursos_notas = db.session.query(Curso, Nota).outerjoin(Nota, 
        db.and_(Nota.curso_id == Curso.id, Nota.alumno_id == current_user.id)
    ).join(CursoAlumno).filter(CursoAlumno.alumno_id == current_user.id).all()
    
    return render_template('alumno/cursos.html', cursos_notas=cursos_notas)
