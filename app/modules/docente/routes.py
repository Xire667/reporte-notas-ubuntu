from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Usuario, Curso, CursoDocente, CursoAlumno, Nota
from . import docente_bp

def docente_required(f):
    """Decorator para requerir rol de docente"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'docente':
            flash('No tienes permisos para acceder a esta página.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@docente_bp.route('/')
@login_required
@docente_required
def dashboard():
    # Obtener cursos asignados al docente
    cursos_asignados = db.session.query(Curso).join(CursoDocente).filter(
        CursoDocente.docente_id == current_user.id
    ).all()
    
    return render_template('docente/dashboard.html', cursos=cursos_asignados)

@docente_bp.route('/cursos/<int:curso_id>/alumnos')
@login_required
@docente_required
def ver_alumnos_curso(curso_id):
    # Verificar que el docente tenga asignado este curso
    curso_docente = CursoDocente.query.filter_by(
        curso_id=curso_id, 
        docente_id=current_user.id
    ).first()
    
    if not curso_docente:
        flash('No tienes acceso a este curso.', 'error')
        return redirect(url_for('docente.dashboard'))
    
    # Obtener alumnos del curso
    alumnos = db.session.query(Usuario).join(CursoAlumno).filter(
        CursoAlumno.curso_id == curso_id
    ).all()
    
    curso = Curso.query.get(curso_id)
    
    return render_template('docente/alumnos_curso.html', 
                         alumnos=alumnos, 
                         curso=curso)

@docente_bp.route('/cursos/<int:curso_id>/notas')
@login_required
@docente_required
def gestionar_notas(curso_id):
    # Verificar que el docente tenga asignado este curso
    curso_docente = CursoDocente.query.filter_by(
        curso_id=curso_id, 
        docente_id=current_user.id
    ).first()
    
    if not curso_docente:
        flash('No tienes acceso a este curso.', 'error')
        return redirect(url_for('docente.dashboard'))
    
    # Obtener alumnos y sus notas
    alumnos_notas = db.session.query(Usuario, Nota).outerjoin(Nota, 
        db.and_(Nota.alumno_id == Usuario.id, Nota.curso_id == curso_id)
    ).join(CursoAlumno).filter(CursoAlumno.curso_id == curso_id).all()
    
    curso = Curso.query.get(curso_id)
    
    return render_template('docente/gestionar_notas.html', 
                         alumnos_notas=alumnos_notas, 
                         curso=curso)

@docente_bp.route('/cursos/<int:curso_id>/notas/guardar', methods=['POST'])
@login_required
@docente_required
def guardar_notas(curso_id):
    # Verificar que el docente tenga asignado este curso
    curso_docente = CursoDocente.query.filter_by(
        curso_id=curso_id, 
        docente_id=current_user.id
    ).first()
    
    if not curso_docente:
        return jsonify({'success': False, 'message': 'No tienes acceso a este curso.'})
    
    try:
        # Obtener datos del formulario
        alumno_id = request.form.get('alumno_id')
        comentarios = request.form.get('comentarios', '')
        estado = request.form.get('estado', 'borrador')
        
        # Obtener el curso para saber cuántos parciales tiene
        curso = Curso.query.get(curso_id)
        if not curso:
            return jsonify({'success': False, 'message': 'Curso no encontrado.'})
        
        # Recopilar notas dinámicamente
        notas_parciales = {}
        for i in range(1, curso.numero_parciales + 1):
            notas_parciales[f'parcial{i}'] = request.form.get(f'parcial{i}')
        
        # Validar que se proporcione el alumno_id
        if not alumno_id:
            return jsonify({'success': False, 'message': 'ID de alumno requerido.'})
        
        # Verificar que el alumno esté matriculado en el curso
        matricula = CursoAlumno.query.filter_by(
            curso_id=curso_id,
            alumno_id=alumno_id
        ).first()
        
        if not matricula:
            return jsonify({'success': False, 'message': 'El alumno no está matriculado en este curso.'})
        
        # Convertir y validar notas
        try:
            notas_validadas = {}
            for i in range(1, curso.numero_parciales + 1):
                valor = notas_parciales[f'parcial{i}']
                notas_validadas[f'parcial{i}'] = float(valor) if valor and valor.strip() != '' else None
        except ValueError:
            return jsonify({'success': False, 'message': 'Error en el formato de las notas. Verifica que sean números válidos.'})
        
        # Validar que al menos una nota tenga valor
        tiene_notas = any(nota is not None for nota in notas_validadas.values())
        if not tiene_notas:
            return jsonify({'success': False, 'message': 'Debe ingresar al menos una nota.'})
        
        # Validar rango de notas (0-20)
        for nota_val in notas_validadas.values():
            if nota_val is not None and (nota_val < 0 or nota_val > 20):
                return jsonify({'success': False, 'message': 'Las notas deben estar entre 0 y 20.'})
        
        # Buscar o crear la nota
        nota = Nota.query.filter_by(
            curso_id=curso_id, 
            alumno_id=alumno_id
        ).first()
        
        if not nota:
            nota = Nota(
                curso_id=curso_id,
                alumno_id=alumno_id,
                docente_id=current_user.id
            )
            db.session.add(nota)
        
        # Actualizar notas dinámicamente
        for i in range(1, curso.numero_parciales + 1):
            valor = notas_validadas[f'parcial{i}']
            setattr(nota, f'parcial{i}', valor if valor is not None else 0.0)
        
        # Si el curso tiene menos de 4 parciales, poner los restantes en 0
        for i in range(curso.numero_parciales + 1, 5):  # máximo 4 parciales en el modelo
            setattr(nota, f'parcial{i}', 0.0)
        
        nota.comentarios = comentarios
        nota.estado = estado
        
        # Calcular nota final
        nota.calcular_nota_final()
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Notas guardadas correctamente.',
            'nota_final': nota.nota_final,
            'estado': nota.estado
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al guardar notas: {e}")  # Para debugging
        return jsonify({'success': False, 'message': f'Error al guardar las notas: {str(e)}'})

@docente_bp.route('/cursos/<int:curso_id>/notas/<int:alumno_id>')
@login_required
@docente_required
def ver_nota_alumno(curso_id, alumno_id):
    # Verificar que el docente tenga asignado este curso
    curso_docente = CursoDocente.query.filter_by(
        curso_id=curso_id, 
        docente_id=current_user.id
    ).first()
    
    if not curso_docente:
        flash('No tienes acceso a este curso.', 'error')
        return redirect(url_for('docente.dashboard'))
    
    # Obtener datos del alumno y su nota
    alumno = Usuario.query.get(alumno_id)
    curso = Curso.query.get(curso_id)
    nota = Nota.query.filter_by(
        curso_id=curso_id, 
        alumno_id=alumno_id
    ).first()
    
    return render_template('docente/ver_nota_alumno.html', 
                         alumno=alumno, 
                         curso=curso, 
                         nota=nota)

@docente_bp.route('/cursos/<int:curso_id>/notas/<int:alumno_id>/cambiar-estado', methods=['POST'])
@login_required
@docente_required
def cambiar_estado_nota(curso_id, alumno_id):
    # Verificar que el docente tenga asignado este curso
    curso_docente = CursoDocente.query.filter_by(
        curso_id=curso_id, 
        docente_id=current_user.id
    ).first()
    
    if not curso_docente:
        return jsonify({'success': False, 'message': 'No tienes acceso a este curso.'})
    
    try:
        # Obtener la nota
        nota = Nota.query.filter_by(
            curso_id=curso_id, 
            alumno_id=alumno_id
        ).first()
        
        if not nota:
            return jsonify({'success': False, 'message': 'No se encontró la nota.'})
        
        # Cambiar el estado
        if nota.estado == 'borrador':
            nota.estado = 'publicada'
        else:
            nota.estado = 'borrador'
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Estado cambiado a {nota.estado}.',
            'estado': nota.estado
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al cambiar el estado: {str(e)}'})
