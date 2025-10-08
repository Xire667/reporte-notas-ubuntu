from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Usuario, Curso, CursoAlumno, CursoDocente, Nota, NotaActividades, NotaPracticas, NotaParcial
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
    
    # Obtener nota del curso (solo si está publicada)
    nota = Nota.query.filter_by(
        curso_id=curso_id, 
        alumno_id=current_user.id,
        estado='publicada'
    ).first()
    
    # Obtener curso con información del docente
    curso = db.session.query(Curso).join(CursoDocente).join(Usuario).filter(
        Curso.id == curso_id,
        Usuario.rol == 'docente'
    ).first()
    
    # Si no se encuentra el curso con docente, obtener solo el curso
    if not curso:
        curso = Curso.query.get(curso_id)
    
    # Obtener detalles de las notas si existe la nota principal
    nota_actividades = None
    nota_practicas = None
    nota_parcial = None
    promedio_actividades = 0
    promedio_practicas = 0
    promedio_parciales = 0
    
    if nota:
        # Obtener actividades
        if nota.nota_actividades_id:
            nota_actividades = NotaActividades.query.get(nota.nota_actividades_id)
            if nota_actividades:
                actividades_vals = [
                    nota_actividades.actividad1, nota_actividades.actividad2,
                    nota_actividades.actividad3, nota_actividades.actividad4,
                    nota_actividades.actividad5, nota_actividades.actividad6,
                    nota_actividades.actividad7, nota_actividades.actividad8
                ]
                actividades_validas = [val for val in actividades_vals if val is not None and val > 0]
                if actividades_validas:
                    promedio_actividades = sum(actividades_validas) / len(actividades_validas)
        
        # Obtener prácticas
        if nota.nota_practicas_id:
            nota_practicas = NotaPracticas.query.get(nota.nota_practicas_id)
            if nota_practicas:
                practicas_vals = [
                    nota_practicas.practica1, nota_practicas.practica2,
                    nota_practicas.practica3, nota_practicas.practica4
                ]
                practicas_validas = [val for val in practicas_vals if val is not None and val > 0]
                if practicas_validas:
                    promedio_practicas = sum(practicas_validas) / len(practicas_validas)
        
        # Obtener parciales
        if nota.nota_parcial_id:
            nota_parcial = NotaParcial.query.get(nota.nota_parcial_id)
            if nota_parcial:
                parciales_vals = [nota_parcial.parcial1, nota_parcial.parcial2]
                parciales_validos = [val for val in parciales_vals if val is not None and val > 0]
                if parciales_validos:
                    promedio_parciales = sum(parciales_validos) / len(parciales_validos)
    
    return render_template('alumno/notas_curso.html', 
                         nota=nota, 
                         curso=curso,
                         nota_actividades=nota_actividades,
                         nota_practicas=nota_practicas,
                         nota_parcial=nota_parcial,
                         promedio_actividades=promedio_actividades,
                         promedio_practicas=promedio_practicas,
                         promedio_parciales=promedio_parciales)

@alumno_bp.route('/cursos')
@login_required
@alumno_required
def ver_cursos():
    # Obtener cursos del alumno con información de notas (solo publicadas)
    cursos_notas = db.session.query(Curso, Nota).outerjoin(Nota, 
        db.and_(
            Nota.curso_id == Curso.id, 
            Nota.alumno_id == current_user.id,
            Nota.estado == 'publicada'
        )
    ).join(CursoAlumno).filter(CursoAlumno.alumno_id == current_user.id).all()
    
    return render_template('alumno/cursos.html', cursos_notas=cursos_notas)
