from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Usuario, Curso, CursoDocente, CursoAlumno, Nota, NotaActividades, NotaPracticas, NotaParcial
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
    """Redirige a la vista de alumnos del curso para seleccionar el alumno específico"""
    return redirect(url_for('docente.ver_alumnos_curso', curso_id=curso_id))

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
        
        # Obtener el curso
        curso = Curso.query.get(curso_id)
        if not curso:
            return jsonify({'success': False, 'message': 'Curso no encontrado.'})
        
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
        
        # Recopilar y validar notas de actividades (8 actividades)
        actividades = {}
        for i in range(1, 9):
            valor = request.form.get(f'actividad{i}')
            try:
                actividades[f'actividad{i}'] = float(valor) if valor and valor.strip() != '' else 0.0
            except ValueError:
                return jsonify({'success': False, 'message': f'Error en el formato de la actividad {i}. Debe ser un número válido.'})
        
        # Recopilar y validar notas de prácticas (4 prácticas)
        practicas = {}
        for i in range(1, 5):
            valor = request.form.get(f'practica{i}')
            try:
                practicas[f'practica{i}'] = float(valor) if valor and valor.strip() != '' else 0.0
            except ValueError:
                return jsonify({'success': False, 'message': f'Error en el formato de la práctica {i}. Debe ser un número válido.'})
        
        # Recopilar y validar notas de parciales (2 parciales)
        parciales = {}
        for i in range(1, 3):
            valor = request.form.get(f'parcial{i}')
            try:
                parciales[f'parcial{i}'] = float(valor) if valor and valor.strip() != '' else 0.0
            except ValueError:
                return jsonify({'success': False, 'message': f'Error en el formato del parcial {i}. Debe ser un número válido.'})
        
        # Validar rango de notas (0-20)
        todas_las_notas = list(actividades.values()) + list(practicas.values()) + list(parciales.values())
        for nota_val in todas_las_notas:
            if nota_val < 0 or nota_val > 20:
                return jsonify({'success': False, 'message': 'Las notas deben estar entre 0 y 20.'})
        
        # Buscar o crear NotaActividades
        nota_actividades = NotaActividades.query.filter_by(
            curso_id=curso_id, 
            alumno_id=alumno_id
        ).first()
        
        if not nota_actividades:
            nota_actividades = NotaActividades(
                curso_id=curso_id,
                alumno_id=alumno_id,
                docente_id=current_user.id
            )
            db.session.add(nota_actividades)
        
        # Actualizar actividades
        for key, value in actividades.items():
            setattr(nota_actividades, key, value)
        nota_actividades.calcular_promedio_actividades()
        
        # Buscar o crear NotaPracticas
        nota_practicas = NotaPracticas.query.filter_by(
            curso_id=curso_id, 
            alumno_id=alumno_id
        ).first()
        
        if not nota_practicas:
            nota_practicas = NotaPracticas(
                curso_id=curso_id,
                alumno_id=alumno_id,
                docente_id=current_user.id
            )
            db.session.add(nota_practicas)
        
        # Actualizar prácticas
        for key, value in practicas.items():
            setattr(nota_practicas, key, value)
        nota_practicas.calcular_promedio_practicas()
        
        # Buscar o crear NotaParcial
        nota_parcial = NotaParcial.query.filter_by(
            curso_id=curso_id, 
            alumno_id=alumno_id
        ).first()
        
        if not nota_parcial:
            nota_parcial = NotaParcial(
                curso_id=curso_id,
                alumno_id=alumno_id,
                docente_id=current_user.id
            )
            db.session.add(nota_parcial)
        
        # Actualizar parciales
        for key, value in parciales.items():
            setattr(nota_parcial, key, value)
        nota_parcial.calcular_promedio_parciales()
        
        # Guardar las notas individuales primero
        db.session.commit()
        
        # Buscar o crear la nota principal
        nota = Nota.query.filter_by(
            curso_id=curso_id, 
            alumno_id=alumno_id
        ).first()
        
        if not nota:
            nota = Nota(
                curso_id=curso_id,
                alumno_id=alumno_id,
                docente_id=current_user.id,
                nota_actividades_id=nota_actividades.id,
                nota_practicas_id=nota_practicas.id,
                nota_parcial_id=nota_parcial.id
            )
            db.session.add(nota)
        else:
            # Actualizar referencias si ya existe
            nota.nota_actividades_id = nota_actividades.id
            nota.nota_practicas_id = nota_practicas.id
            nota.nota_parcial_id = nota_parcial.id
        
        nota.comentarios = comentarios
        nota.estado = estado
        
        # Calcular promedio final
        nota.calcular_promedio_final()
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Notas guardadas correctamente.',
            'promedio_final': nota.promedio_final,
            'promedio_actividades': nota_actividades.promedio_actividades,
            'promedio_practicas': nota_practicas.promedio_practicas,
            'promedio_parciales': nota_parcial.promedio_parciales,
            'estado': nota.estado
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al guardar notas: {e}")  # Para debugging
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'})

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
    
    # Obtener las notas detalladas
    nota_actividades = NotaActividades.query.filter_by(
        curso_id=curso_id, 
        alumno_id=alumno_id
    ).first()
    
    nota_practicas = NotaPracticas.query.filter_by(
        curso_id=curso_id, 
        alumno_id=alumno_id
    ).first()
    
    nota_parcial = NotaParcial.query.filter_by(
        curso_id=curso_id, 
        alumno_id=alumno_id
    ).first()
    
    return render_template('docente/ver_nota_alumno.html', 
                         alumno=alumno, 
                         curso=curso, 
                         nota=nota,
                         nota_actividades=nota_actividades,
                         nota_practicas=nota_practicas,
                         nota_parcial=nota_parcial)

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
