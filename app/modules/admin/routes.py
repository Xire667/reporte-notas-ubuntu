from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Usuario, Curso, CursoDocente, CursoAlumno, CicloAcademico, MatriculaAlumno, Nota
from . import admin_bp

def admin_required(f):
    """Decorator para requerir rol de administrador"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            flash('No tienes permisos para acceder a esta página.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_docentes = Usuario.query.filter_by(rol='docente').count()
    total_alumnos = Usuario.query.filter_by(rol='alumno').count()
    total_cursos = Curso.query.count()
    
    # Contar alumnos matriculados en ciclos (matrículas activas)
    alumnos_matriculados = MatriculaAlumno.query.filter_by(estado='activa').count()
    
    # Contar total de notas registradas
    total_notas = db.session.query(Nota).count()
    
    return render_template('admin/dashboard.html', 
                         total_docentes=total_docentes,
                         total_alumnos=total_alumnos,
                         alumnos_matriculados=alumnos_matriculados,
                         total_cursos=total_cursos,
                         total_notas=total_notas)

# Gestión de Docentes
@admin_bp.route('/docentes')
@login_required
@admin_required
def docentes():
    docentes_data = []
    docentes = Usuario.query.filter_by(rol='docente').all()
    
    for docente in docentes:
        # Verificar relaciones para cada docente
        cursos_asignados = CursoDocente.query.filter_by(docente_id=docente.id).count()
        notas_registradas = Nota.query.filter_by(docente_id=docente.id).count()
        
        # Determinar si se puede desactivar/eliminar
        puede_desactivar = True  # Los docentes siempre se pueden desactivar
        puede_eliminar = cursos_asignados == 0 and notas_registradas == 0
        
        docentes_data.append({
            'docente': docente,
            'cursos_asignados': cursos_asignados,
            'notas_registradas': notas_registradas,
            'puede_desactivar': puede_desactivar,
            'puede_eliminar': puede_eliminar
        })
    
    return render_template('admin/docentes.html', docentes=docentes_data)

@admin_bp.route('/docentes/registrar', methods=['GET', 'POST'])
@login_required
@admin_required
def registrar_docente():
    if request.method == 'POST':
        dni = request.form.get('dni')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if Usuario.query.filter_by(dni=dni).first():
            flash('El DNI ya está registrado.', 'error')
            return render_template('admin/registrar_docente.html')
        
        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado.', 'error')
            return render_template('admin/registrar_docente.html')
        
        docente = Usuario(
            dni=dni,
            nombre=nombre,
            apellido=apellido,
            email=email,
            rol='docente'
        )
        docente.set_password(password)
        
        try:
            db.session.add(docente)
            db.session.commit()
            flash('Docente registrado correctamente.', 'success')
            return redirect(url_for('admin.docentes'))
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar el docente.', 'error')
    
    return render_template('admin/registrar_docente.html')

# Gestión de Cursos
@admin_bp.route('/cursos')
@login_required
@admin_required
def cursos():
    cursos_data = []
    cursos = db.session.query(Curso, CicloAcademico).outerjoin(CicloAcademico).all()
    
    for curso, ciclo in cursos:
        # Verificar relaciones para cada curso
        docentes_asignados = CursoDocente.query.filter_by(curso_id=curso.id).count()
        alumnos_matriculados = CursoAlumno.query.filter_by(curso_id=curso.id).count()
        notas_registradas = Nota.query.filter_by(curso_id=curso.id).count()
        
        # Determinar si se puede desactivar/eliminar
        puede_desactivar = docentes_asignados == 0 and alumnos_matriculados == 0 and notas_registradas == 0
        puede_eliminar = puede_desactivar
        
        cursos_data.append({
            'curso': curso,
            'ciclo': ciclo,
            'docentes_asignados': docentes_asignados,
            'alumnos_matriculados': alumnos_matriculados,
            'notas_registradas': notas_registradas,
            'puede_desactivar': puede_desactivar,
            'puede_eliminar': puede_eliminar
        })
    
    return render_template('admin/cursos.html', cursos=cursos_data)

@admin_bp.route('/cursos/registrar', methods=['GET', 'POST'])
@login_required
@admin_required
def registrar_curso():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        codigo = request.form.get('codigo')
        descripcion = request.form.get('descripcion')
        creditos = int(request.form.get('creditos', 3))
        ciclo_academico_id = request.form.get('ciclo_academico_id')
        
        if Curso.query.filter_by(codigo=codigo).first():
            flash('El código del curso ya existe.', 'error')
            return render_template('admin/registrar_curso.html', ciclos=CicloAcademico.query.filter_by(activo=True).all())
        
        curso = Curso(
            nombre=nombre,
            codigo=codigo,
            descripcion=descripcion,
            creditos=creditos,
            ciclo_academico_id=ciclo_academico_id if ciclo_academico_id else None
        )
        
        try:
            db.session.add(curso)
            db.session.commit()
            flash('Curso registrado correctamente.', 'success')
            return redirect(url_for('admin.cursos'))
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar el curso.', 'error')
    
    ciclos = CicloAcademico.query.filter_by(activo=True).order_by(CicloAcademico.orden).all()
    return render_template('admin/registrar_curso.html', ciclos=ciclos)

@admin_bp.route('/cursos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_curso(id):
    curso = Curso.query.get_or_404(id)
    
    if request.method == 'POST':
        curso.nombre = request.form.get('nombre')
        curso.codigo = request.form.get('codigo')
        curso.descripcion = request.form.get('descripcion')
        curso.creditos = int(request.form.get('creditos', 3))
        curso.ciclo_academico_id = request.form.get('ciclo_academico_id') if request.form.get('ciclo_academico_id') else None
        
        # Verificar que el código no esté en uso por otro curso
        if Curso.query.filter(Curso.codigo == curso.codigo, Curso.id != id).first():
            flash('El código del curso ya está en uso por otro curso.', 'error')
            return render_template('admin/editar_curso.html', curso=curso, ciclos=CicloAcademico.query.filter_by(activo=True).order_by(CicloAcademico.orden).all())
        
        try:
            db.session.commit()
            flash('Curso actualizado correctamente.', 'success')
            return redirect(url_for('admin.cursos'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el curso.', 'error')
    
    ciclos = CicloAcademico.query.filter_by(activo=True).order_by(CicloAcademico.orden).all()
    return render_template('admin/editar_curso.html', curso=curso, ciclos=ciclos)

@admin_bp.route('/cursos/toggle-activo/<int:id>', methods=['POST'])
@login_required
@admin_required
def toggle_activo_curso(id):
    curso = Curso.query.get_or_404(id)
    
    try:
        # Verificar si tiene docentes asignados
        docentes_asignados = CursoDocente.query.filter_by(curso_id=id).count()
        if docentes_asignados > 0:
            return jsonify({
                'success': False, 
                'message': f'No se puede desactivar el curso porque tiene {docentes_asignados} docente(s) asignado(s).'
            })
        
        # Verificar si tiene alumnos matriculados
        alumnos_matriculados = CursoAlumno.query.filter_by(curso_id=id).count()
        if alumnos_matriculados > 0:
            return jsonify({
                'success': False, 
                'message': f'No se puede desactivar el curso porque tiene {alumnos_matriculados} alumno(s) matriculado(s).'
            })
        
        # Verificar si tiene notas registradas
        notas_registradas = Nota.query.filter_by(curso_id=id).count()
        if notas_registradas > 0:
            return jsonify({
                'success': False, 
                'message': f'No se puede desactivar el curso porque tiene {notas_registradas} nota(s) registrada(s).'
            })
        
        curso.activo = not curso.activo
        db.session.commit()
        
        estado = 'activado' if curso.activo else 'desactivado'
        return jsonify({
            'success': True, 
            'message': f'Curso {estado} correctamente.',
            'activo': curso.activo
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al cambiar el estado del curso.'})

@admin_bp.route('/cursos/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_required
def eliminar_curso(id):
    curso = Curso.query.get_or_404(id)
    
    try:
        # Verificar si tiene docentes asignados
        docentes_asignados = CursoDocente.query.filter_by(curso_id=id).count()
        if docentes_asignados > 0:
            return jsonify({
                'success': False, 
                'message': f'No se puede eliminar el curso porque tiene {docentes_asignados} docente(s) asignado(s).'
            })
        
        # Verificar si tiene alumnos matriculados
        alumnos_matriculados = CursoAlumno.query.filter_by(curso_id=id).count()
        if alumnos_matriculados > 0:
            return jsonify({
                'success': False, 
                'message': f'No se puede eliminar el curso porque tiene {alumnos_matriculados} alumno(s) matriculado(s).'
            })
        
        # Verificar si tiene notas registradas
        notas_registradas = Nota.query.filter_by(curso_id=id).count()
        if notas_registradas > 0:
            return jsonify({
                'success': False, 
                'message': f'No se puede eliminar el curso porque tiene {notas_registradas} nota(s) registrada(s).'
            })
        
        db.session.delete(curso)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Curso eliminado correctamente.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al eliminar el curso.'})

# Asignar cursos a docentes
@admin_bp.route('/asignar-cursos', methods=['GET', 'POST'])
@login_required
@admin_required
def asignar_cursos():
    if request.method == 'POST':
        curso_id = request.form.get('curso_id')
        docente_id = request.form.get('docente_id')
        
        # Verificar que no esté ya asignado
        if CursoDocente.query.filter_by(curso_id=curso_id, docente_id=docente_id).first():
            flash('Este curso ya está asignado a este docente.', 'error')
        else:
            asignacion = CursoDocente(curso_id=curso_id, docente_id=docente_id)
            db.session.add(asignacion)
            db.session.commit()
            flash('Curso asignado correctamente.', 'success')
        
        return redirect(url_for('admin.asignar_cursos'))
    
    cursos = Curso.query.filter_by(activo=True).all()
    docentes = Usuario.query.filter_by(rol='docente', activo=True).all()
    asignaciones = db.session.query(CursoDocente, Curso, Usuario).join(Curso).join(Usuario).all()
    
    return render_template('admin/asignar_cursos.html', 
                         cursos=cursos, 
                         docentes=docentes, 
                         asignaciones=asignaciones)

# Gestión de Alumnos
@admin_bp.route('/alumnos')
@login_required
@admin_required
def alumnos():
    alumnos_data = []
    alumnos = db.session.query(Usuario).filter_by(rol='alumno').all()
    
    for alumno in alumnos:
        # Verificar relaciones para cada alumno
        cursos_matriculados = CursoAlumno.query.filter_by(alumno_id=alumno.id).count()
        matriculas_ciclos = MatriculaAlumno.query.filter_by(alumno_id=alumno.id).count()
        notas_registradas = Nota.query.filter_by(alumno_id=alumno.id).count()
        
        # Obtener matrícula activa
        matricula_activa = MatriculaAlumno.query.filter_by(
            alumno_id=alumno.id, 
            estado='activa'
        ).first()
        
        # Determinar si se puede desactivar/eliminar
        puede_desactivar = True  # Los alumnos siempre se pueden desactivar
        puede_eliminar = cursos_matriculados == 0 and matriculas_ciclos == 0 and notas_registradas == 0
        
        alumnos_data.append({
            'alumno': alumno,
            'matricula_activa': matricula_activa,
            'cursos_matriculados': cursos_matriculados,
            'matriculas_ciclos': matriculas_ciclos,
            'notas_registradas': notas_registradas,
            'puede_desactivar': puede_desactivar,
            'puede_eliminar': puede_eliminar
        })
    
    return render_template('admin/alumnos.html', alumnos=alumnos_data)

@admin_bp.route('/alumnos/registrar', methods=['GET', 'POST'])
@login_required
@admin_required
def registrar_alumno():
    if request.method == 'POST':
        dni = request.form.get('dni')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if Usuario.query.filter_by(dni=dni).first():
            flash('El DNI ya está registrado.', 'error')
            return render_template('admin/registrar_alumno.html')
        
        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado.', 'error')
            return render_template('admin/registrar_alumno.html')
        
        alumno = Usuario(
            dni=dni,
            nombre=nombre,
            apellido=apellido,
            email=email,
            rol='alumno'
        )
        alumno.set_password(password)
        
        try:
            db.session.add(alumno)
            db.session.commit()
            flash('Alumno registrado correctamente.', 'success')
            return redirect(url_for('admin.alumnos'))
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar el alumno.', 'error')
    
    return render_template('admin/registrar_alumno.html')


# Funcionalidades adicionales para docentes
@admin_bp.route('/docentes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_docente(id):
    docente = Usuario.query.get_or_404(id)
    
    if docente.rol != 'docente':
        flash('El usuario no es un docente.', 'error')
        return redirect(url_for('admin.docentes'))
    
    if request.method == 'POST':
        docente.dni = request.form.get('dni')
        docente.nombre = request.form.get('nombre')
        docente.apellido = request.form.get('apellido')
        docente.email = request.form.get('email')
        
        # Verificar DNI único
        if Usuario.query.filter(Usuario.dni == docente.dni, Usuario.id != id).first():
            flash('El DNI ya está registrado por otro usuario.', 'error')
            return render_template('admin/editar_docente.html', docente=docente)
        
        # Verificar email único
        if Usuario.query.filter(Usuario.email == docente.email, Usuario.id != id).first():
            flash('El email ya está registrado por otro usuario.', 'error')
            return render_template('admin/editar_docente.html', docente=docente)
        
        # Actualizar contraseña si se proporciona
        nueva_password = request.form.get('password')
        if nueva_password:
            docente.set_password(nueva_password)
        
        try:
            db.session.commit()
            flash('Docente actualizado correctamente.', 'success')
            return redirect(url_for('admin.docentes'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el docente.', 'error')
    
    return render_template('admin/editar_docente.html', docente=docente)

@admin_bp.route('/docentes/toggle-activo/<int:id>', methods=['POST'])
@login_required
@admin_required
def toggle_activo_docente(id):
    docente = Usuario.query.get_or_404(id)
    
    if docente.rol != 'docente':
        return jsonify({'success': False, 'message': 'El usuario no es un docente.'})
    
    try:
        docente.activo = not docente.activo
        db.session.commit()
        
        estado = 'activado' if docente.activo else 'desactivado'
        return jsonify({
            'success': True, 
            'message': f'Docente {estado} correctamente.',
            'activo': docente.activo
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al cambiar el estado del docente.'})

@admin_bp.route('/docentes/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_required
def eliminar_docente(id):
    docente = Usuario.query.get_or_404(id)
    
    if docente.rol != 'docente':
        return jsonify({'success': False, 'message': 'El usuario no es un docente.'})
    
    try:
        # Verificar si tiene cursos asignados
        cursos_asignados = CursoDocente.query.filter_by(docente_id=id).count()
        if cursos_asignados > 0:
            return jsonify({
                'success': False, 
                'message': f'No se puede eliminar el docente porque tiene {cursos_asignados} curso(s) asignado(s).'
            })
        
        # Verificar si tiene notas registradas
        notas_registradas = Nota.query.filter_by(docente_id=id).count()
        if notas_registradas > 0:
            return jsonify({
                'success': False, 
                'message': f'No se puede eliminar el docente porque tiene {notas_registradas} nota(s) registrada(s).'
            })
        
        db.session.delete(docente)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Docente eliminado correctamente.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al eliminar el docente.'})

# Nuevas funcionalidades para docentes
@admin_bp.route('/docentes/<int:id>/cursos')
@login_required
@admin_required
def ver_cursos_docente(id):
    """Ver cursos asignados a un docente específico"""
    docente = Usuario.query.get_or_404(id)
    
    if docente.rol != 'docente':
        flash('El usuario no es un docente.', 'error')
        return redirect(url_for('admin.docentes'))
    
    # Obtener cursos asignados con información adicional
    cursos_data = []
    asignaciones = db.session.query(CursoDocente, Curso, CicloAcademico).join(
        Curso, CursoDocente.curso_id == Curso.id
    ).outerjoin(
        CicloAcademico, Curso.ciclo_academico_id == CicloAcademico.id
    ).filter(
        CursoDocente.docente_id == id
    ).all()
    
    for asignacion, curso, ciclo in asignaciones:
        # Obtener estadísticas del curso
        total_alumnos = CursoAlumno.query.filter_by(curso_id=curso.id).count()
        notas_registradas = Nota.query.filter_by(curso_id=curso.id, docente_id=id).count()
        notas_publicadas = Nota.query.filter_by(curso_id=curso.id, docente_id=id, estado='publicada').count()
        
        # Calcular promedio del curso
        notas_finales = [nota.nota_final for nota in Nota.query.filter_by(curso_id=curso.id, docente_id=id).all() if nota.nota_final > 0]
        promedio_curso = sum(notas_finales) / len(notas_finales) if notas_finales else 0
        
        cursos_data.append({
            'curso': curso,
            'ciclo': ciclo,
            'asignacion': asignacion,
            'total_alumnos': total_alumnos,
            'notas_registradas': notas_registradas,
            'notas_publicadas': notas_publicadas,
            'promedio_curso': promedio_curso
        })
    
    return render_template('admin/cursos_docente.html', 
                         docente=docente, 
                         cursos=cursos_data)

@admin_bp.route('/docentes/<int:id>/estadisticas')
@login_required
@admin_required
def estadisticas_docente(id):
    """Ver estadísticas detalladas de un docente"""
    docente = Usuario.query.get_or_404(id)
    
    if docente.rol != 'docente':
        flash('El usuario no es un docente.', 'error')
        return redirect(url_for('admin.docentes'))
    
    # Estadísticas generales
    total_cursos = CursoDocente.query.filter_by(docente_id=id).count()
    
    # Obtener total de alumnos de manera más simple
    cursos_docente_ids = [cd.curso_id for cd in CursoDocente.query.filter_by(docente_id=id).all()]
    total_alumnos = CursoAlumno.query.filter(CursoAlumno.curso_id.in_(cursos_docente_ids)).count()
    
    total_notas = Nota.query.filter_by(docente_id=id).count()
    notas_publicadas = Nota.query.filter_by(docente_id=id, estado='publicada').count()
    
    # Estadísticas por curso
    cursos_estadisticas = []
    asignaciones = db.session.query(CursoDocente, Curso).join(
        Curso, CursoDocente.curso_id == Curso.id
    ).filter(
        CursoDocente.docente_id == id
    ).all()
    
    for asignacion, curso in asignaciones:
        alumnos_curso = CursoAlumno.query.filter_by(curso_id=curso.id).count()
        notas_curso = Nota.query.filter_by(curso_id=curso.id, docente_id=id).count()
        notas_publicadas_curso = Nota.query.filter_by(curso_id=curso.id, docente_id=id, estado='publicada').count()
        
        # Calcular promedio del curso
        notas_finales = [nota.nota_final for nota in Nota.query.filter_by(curso_id=curso.id, docente_id=id).all() if nota.nota_final > 0]
        promedio_curso = sum(notas_finales) / len(notas_finales) if notas_finales else 0
        
        cursos_estadisticas.append({
            'curso': curso,
            'alumnos': alumnos_curso,
            'notas_total': notas_curso,
            'notas_publicadas': notas_publicadas_curso,
            'promedio': promedio_curso
        })
    
    # Calcular promedio general
    todas_las_notas = [nota.nota_final for nota in Nota.query.filter_by(docente_id=id).all() if nota.nota_final > 0]
    promedio_general = sum(todas_las_notas) / len(todas_las_notas) if todas_las_notas else 0
    
    return render_template('admin/estadisticas_docente.html',
                         docente=docente,
                         total_cursos=total_cursos,
                         total_alumnos=total_alumnos,
                         total_notas=total_notas,
                         notas_publicadas=notas_publicadas,
                         promedio_general=promedio_general,
                         cursos_estadisticas=cursos_estadisticas)

@admin_bp.route('/docentes/<int:id>/alumnos')
@login_required
@admin_required
def ver_alumnos_docente(id):
    """Ver todos los alumnos de un docente (de todos sus cursos)"""
    docente = Usuario.query.get_or_404(id)
    
    if docente.rol != 'docente':
        flash('El usuario no es un docente.', 'error')
        return redirect(url_for('admin.docentes'))
    
    # Obtener alumnos únicos de todos los cursos del docente
    alumnos_data = []
    cursos_docente = db.session.query(Curso).join(
        CursoDocente, Curso.id == CursoDocente.curso_id
    ).filter(
        CursoDocente.docente_id == id
    ).all()
    
    # Crear un diccionario para evitar duplicados
    alumnos_dict = {}
    
    for curso in cursos_docente:
        # Obtener alumnos de este curso
        curso_alumnos = db.session.query(CursoAlumno, Usuario).join(
            Usuario, CursoAlumno.alumno_id == Usuario.id
        ).filter(
            CursoAlumno.curso_id == curso.id
        ).all()
        
        for curso_alumno, alumno in curso_alumnos:
            if alumno.id not in alumnos_dict:
                # Obtener información adicional del alumno
                notas_alumno = Nota.query.filter_by(alumno_id=alumno.id, docente_id=id).count()
                promedio_alumno = 0
                
                # Calcular promedio del alumno con este docente
                notas_finales = [nota.nota_final for nota in Nota.query.filter_by(alumno_id=alumno.id, docente_id=id).all() if nota.nota_final > 0]
                if notas_finales:
                    promedio_alumno = sum(notas_finales) / len(notas_finales)
                
                alumnos_dict[alumno.id] = {
                    'alumno': alumno,
                    'cursos': [curso.nombre],
                    'notas_total': notas_alumno,
                    'promedio': promedio_alumno
                }
            else:
                # Agregar curso a la lista si no está ya
                if curso.nombre not in alumnos_dict[alumno.id]['cursos']:
                    alumnos_dict[alumno.id]['cursos'].append(curso.nombre)
    
    # Convertir diccionario a lista
    alumnos_data = list(alumnos_dict.values())
    
    return render_template('admin/alumnos_docente.html',
                         docente=docente,
                         alumnos=alumnos_data)

@admin_bp.route('/docentes/<int:id>/notas')
@login_required
@admin_required
def ver_notas_docente(id):
    """Ver todas las notas registradas por un docente"""
    docente = Usuario.query.get_or_404(id)
    
    if docente.rol != 'docente':
        flash('El usuario no es un docente.', 'error')
        return redirect(url_for('admin.docentes'))
    
    # Obtener todas las notas del docente con información adicional
    from sqlalchemy.orm import aliased
    Alumno = aliased(Usuario)
    
    notas = db.session.query(Nota, Curso, Alumno).join(
        Curso, Nota.curso_id == Curso.id
    ).join(
        Alumno, Nota.alumno_id == Alumno.id
    ).filter(Nota.docente_id == id).order_by(Curso.nombre, Alumno.nombre).all()
    
    # Estadísticas
    total_notas = len(notas)
    notas_publicadas = len([n for n in notas if n[0].estado == 'publicada'])
    notas_borrador = len([n for n in notas if n[0].estado == 'borrador'])
    
    # Calcular promedio general
    notas_finales = [nota[0].nota_final for nota in notas if nota[0].nota_final > 0]
    promedio_general = sum(notas_finales) / len(notas_finales) if notas_finales else 0
    
    return render_template('admin/notas_docente.html',
                         docente=docente,
                         notas=notas,
                         total_notas=total_notas,
                         notas_publicadas=notas_publicadas,
                         notas_borrador=notas_borrador,
                         promedio_general=promedio_general)

@admin_bp.route('/docentes/<int:id>/desasignar-curso/<int:curso_id>', methods=['POST'])
@login_required
@admin_required
def desasignar_curso_docente(id, curso_id):
    """Desasignar un curso de un docente"""
    docente = Usuario.query.get_or_404(id)
    curso = Curso.query.get_or_404(curso_id)
    
    if docente.rol != 'docente':
        return jsonify({'success': False, 'message': 'El usuario no es un docente.'})
    
    try:
        # Verificar que la asignación existe
        asignacion = CursoDocente.query.filter_by(docente_id=id, curso_id=curso_id).first()
        if not asignacion:
            return jsonify({'success': False, 'message': 'El docente no está asignado a este curso.'})
        
        # Verificar si tiene notas registradas
        notas_registradas = Nota.query.filter_by(docente_id=id, curso_id=curso_id).count()
        if notas_registradas > 0:
            return jsonify({
                'success': False, 
                'message': f'No se puede desasignar el curso porque el docente tiene {notas_registradas} nota(s) registrada(s) en este curso.'
            })
        
        db.session.delete(asignacion)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Curso "{curso.nombre}" desasignado correctamente del docente.'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al desasignar el curso.'})

# Funcionalidades adicionales para alumnos
@admin_bp.route('/alumnos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_alumno(id):
    alumno = Usuario.query.get_or_404(id)
    
    if alumno.rol != 'alumno':
        flash('El usuario no es un alumno.', 'error')
        return redirect(url_for('admin.alumnos'))
    
    if request.method == 'POST':
        alumno.dni = request.form.get('dni')
        alumno.nombre = request.form.get('nombre')
        alumno.apellido = request.form.get('apellido')
        alumno.email = request.form.get('email')
        
        # Verificar DNI único
        if Usuario.query.filter(Usuario.dni == alumno.dni, Usuario.id != id).first():
            flash('El DNI ya está registrado por otro usuario.', 'error')
            return render_template('admin/editar_alumno.html', alumno=alumno)
        
        # Verificar email único
        if Usuario.query.filter(Usuario.email == alumno.email, Usuario.id != id).first():
            flash('El email ya está registrado por otro usuario.', 'error')
            return render_template('admin/editar_alumno.html', alumno=alumno)
        
        # Actualizar contraseña si se proporciona
        nueva_password = request.form.get('password')
        if nueva_password:
            alumno.set_password(nueva_password)
        
        try:
            db.session.commit()
            flash('Alumno actualizado correctamente.', 'success')
            return redirect(url_for('admin.alumnos'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el alumno.', 'error')
    
    return render_template('admin/editar_alumno.html', alumno=alumno)

@admin_bp.route('/alumnos/toggle-activo/<int:id>', methods=['POST'])
@login_required
@admin_required
def toggle_activo_alumno(id):
    alumno = Usuario.query.get_or_404(id)
    
    if alumno.rol != 'alumno':
        return jsonify({'success': False, 'message': 'El usuario no es un alumno.'})
    
    try:
        alumno.activo = not alumno.activo
        db.session.commit()
        
        estado = 'activado' if alumno.activo else 'desactivado'
        return jsonify({
            'success': True, 
            'message': f'Alumno {estado} correctamente.',
            'activo': alumno.activo
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al cambiar el estado del alumno.'})

@admin_bp.route('/alumnos/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_required
def eliminar_alumno(id):
    alumno = Usuario.query.get_or_404(id)
    
    if alumno.rol != 'alumno':
        return jsonify({'success': False, 'message': 'El usuario no es un alumno.'})
    
    try:
        # Verificar si tiene cursos matriculados
        cursos_matriculados = CursoAlumno.query.filter_by(alumno_id=id).count()
        if cursos_matriculados > 0:
            return jsonify({
                'success': False, 
                'message': f'No se puede eliminar el alumno porque está matriculado en {cursos_matriculados} curso(s).'
            })
        
        # Verificar si tiene matrículas en ciclos
        matriculas_ciclos = MatriculaAlumno.query.filter_by(alumno_id=id).count()
        if matriculas_ciclos > 0:
            return jsonify({
                'success': False, 
                'message': f'No se puede eliminar el alumno porque está matriculado en {matriculas_ciclos} ciclo(s) académico(s).'
            })
        
        # Verificar si tiene notas registradas
        notas_registradas = Nota.query.filter_by(alumno_id=id).count()
        if notas_registradas > 0:
            return jsonify({
                'success': False, 
                'message': f'No se puede eliminar el alumno porque tiene {notas_registradas} nota(s) registrada(s).'
            })
        
        db.session.delete(alumno)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Alumno eliminado correctamente.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al eliminar el alumno.'})

@admin_bp.route('/alumnos/por-ciclo')
@login_required
@admin_required
def alumnos_por_ciclo():
    """Mostrar alumnos agrupados por ciclos académicos"""
    # Obtener todos los ciclos activos
    ciclos = CicloAcademico.query.filter_by(activo=True).order_by(CicloAcademico.orden).all()
    
    # Obtener el ciclo seleccionado (si se proporciona)
    ciclo_id = request.args.get('ciclo_id')
    ciclo_seleccionado = None
    alumnos_ciclo = []
    
    if ciclo_id:
        ciclo_seleccionado = CicloAcademico.query.get(ciclo_id)
        if ciclo_seleccionado:
            # Obtener alumnos matriculados en este ciclo
            matriculas = MatriculaAlumno.query.filter_by(
                ciclo_academico_id=ciclo_id,
                estado='activa'
            ).all()
            
            for matricula in matriculas:
                alumno = matricula.alumno
                # Obtener información adicional del alumno
                cursos_matriculados = CursoAlumno.query.filter_by(alumno_id=alumno.id).count()
                notas_registradas = Nota.query.filter_by(alumno_id=alumno.id).count()
                
                alumnos_ciclo.append({
                    'alumno': alumno,
                    'matricula': matricula,
                    'cursos_matriculados': cursos_matriculados,
                    'notas_registradas': notas_registradas
                })
    
    return render_template('admin/alumnos_por_ciclo.html', 
                         ciclos=ciclos,
                         ciclo_seleccionado=ciclo_seleccionado,
                         alumnos_ciclo=alumnos_ciclo)

@admin_bp.route('/alumnos/editar-matricula/<int:alumno_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_matricula_alumno(alumno_id):
    """Editar la matrícula de un alumno (cambiar de ciclo)"""
    alumno = Usuario.query.get_or_404(alumno_id)
    
    if alumno.rol != 'alumno':
        flash('El usuario no es un alumno.', 'error')
        return redirect(url_for('admin.alumnos'))
    
    # Obtener la matrícula activa del alumno
    matricula_activa = MatriculaAlumno.query.filter_by(
        alumno_id=alumno_id, 
        estado='activa'
    ).first()
    
    if request.method == 'POST':
        nuevo_ciclo_id = request.form.get('ciclo_id')
        forzar_cambio = request.form.get('forzar_cambio') == 'on'
        
        if not nuevo_ciclo_id:
            flash('Selecciona un ciclo válido.', 'error')
            return render_template('admin/editar_matricula.html', 
                                 alumno=alumno, 
                                 matricula_activa=matricula_activa,
                                 ciclos=CicloAcademico.query.filter_by(activo=True).order_by(CicloAcademico.orden).all())
        
        nuevo_ciclo = CicloAcademico.query.get(nuevo_ciclo_id)
        if not nuevo_ciclo:
            flash('El ciclo seleccionado no existe.', 'error')
            return render_template('admin/editar_matricula.html', 
                                 alumno=alumno, 
                                 matricula_activa=matricula_activa,
                                 ciclos=CicloAcademico.query.filter_by(activo=True).order_by(CicloAcademico.orden).all())
        
        # Verificar si ya está matriculado en el nuevo ciclo
        if MatriculaAlumno.query.filter_by(
            alumno_id=alumno_id, 
            ciclo_academico_id=nuevo_ciclo_id,
            estado='activa'
        ).first():
            flash('El alumno ya está matriculado en este ciclo.', 'error')
            return render_template('admin/editar_matricula.html', 
                                 alumno=alumno, 
                                 matricula_activa=matricula_activa,
                                 ciclos=CicloAcademico.query.filter_by(activo=True).order_by(CicloAcademico.orden).all())
        
        try:
            # Si tiene matrícula activa, desactivarla
            if matricula_activa:
                matricula_activa.estado = 'suspendida'
                flash(f'Matrícula anterior en "{matricula_activa.ciclo_academico.nombre}" suspendida.', 'info')
            
            # Crear nueva matrícula
            nueva_matricula = MatriculaAlumno(
                alumno_id=alumno_id,
                ciclo_academico_id=nuevo_ciclo_id
            )
            db.session.add(nueva_matricula)
            
            # Si se solicita forzar el cambio, matricular automáticamente en los cursos del nuevo ciclo
            if forzar_cambio:
                cursos_nuevo_ciclo = Curso.query.filter_by(ciclo_academico_id=nuevo_ciclo_id).all()
                cursos_matriculados = 0
                
                for curso in cursos_nuevo_ciclo:
                    # Verificar que no esté ya matriculado en el curso
                    if not CursoAlumno.query.filter_by(curso_id=curso.id, alumno_id=alumno_id).first():
                        curso_alumno = CursoAlumno(curso_id=curso.id, alumno_id=alumno_id)
                        db.session.add(curso_alumno)
                        cursos_matriculados += 1
                
                if cursos_matriculados > 0:
                    flash(f'Alumno matriculado automáticamente en {cursos_matriculados} curso(s) del nuevo ciclo.', 'info')
            
            db.session.commit()
            flash(f'Matrícula actualizada correctamente. Alumno ahora está en "{nuevo_ciclo.nombre}".', 'success')
            return redirect(url_for('admin.alumnos_por_ciclo', ciclo_id=nuevo_ciclo_id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar la matrícula.', 'error')
    
    ciclos = CicloAcademico.query.filter_by(activo=True).order_by(CicloAcademico.orden).all()
    return render_template('admin/editar_matricula.html', 
                         alumno=alumno, 
                         matricula_activa=matricula_activa,
                         ciclos=ciclos)

@admin_bp.route('/alumnos/suspender-matricula/<int:alumno_id>', methods=['POST'])
@login_required
@admin_required
def suspender_matricula_alumno(alumno_id):
    """Suspender la matrícula activa de un alumno"""
    alumno = Usuario.query.get_or_404(alumno_id)
    
    if alumno.rol != 'alumno':
        return jsonify({'success': False, 'message': 'El usuario no es un alumno.'})
    
    matricula_activa = MatriculaAlumno.query.filter_by(
        alumno_id=alumno_id, 
        estado='activa'
    ).first()
    
    if not matricula_activa:
        return jsonify({'success': False, 'message': 'El alumno no tiene matrícula activa.'})
    
    try:
        matricula_activa.estado = 'suspendida'
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Matrícula en "{matricula_activa.ciclo_academico.nombre}" suspendida correctamente.'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al suspender la matrícula.'})

# Gestión de Notas para Administradores
@admin_bp.route('/notas')
@login_required
@admin_required
def ver_notas():
    """Vista principal de notas para administradores"""
    # Obtener filtros de la URL
    ciclo_id = request.args.get('ciclo_id')
    curso_id = request.args.get('curso_id')
    alumno_id = request.args.get('alumno_id')
    estado = request.args.get('estado', 'todas')
    
    # Construir query base con alias para evitar conflicto de nombres
    from sqlalchemy.orm import aliased
    Alumno = aliased(Usuario)
    Docente = aliased(Usuario)
    
    query = db.session.query(Nota, Curso, Alumno, Docente).join(Curso).join(
        Alumno, Nota.alumno_id == Alumno.id
    ).join(Docente, Nota.docente_id == Docente.id)
    
    # Aplicar filtros
    if ciclo_id:
        query = query.filter(Curso.ciclo_academico_id == ciclo_id)
    
    if curso_id:
        query = query.filter(Nota.curso_id == curso_id)
    
    if alumno_id:
        query = query.filter(Nota.alumno_id == alumno_id)
    
    if estado != 'todas':
        query = query.filter(Nota.estado == estado)
    
    # Ordenar por fecha de actualización
    notas = query.order_by(Nota.fecha_actualizacion.desc()).all()
    
    # Obtener datos para los filtros
    ciclos = CicloAcademico.query.filter_by(activo=True).order_by(CicloAcademico.orden).all()
    cursos = Curso.query.filter_by(activo=True).order_by(Curso.nombre).all()
    alumnos = Usuario.query.filter_by(rol='alumno', activo=True).order_by(Usuario.nombre).all()
    
    # Obtener ciclo y curso seleccionados
    ciclo_seleccionado = CicloAcademico.query.get(ciclo_id) if ciclo_id else None
    curso_seleccionado = Curso.query.get(curso_id) if curso_id else None
    alumno_seleccionado = Usuario.query.get(alumno_id) if alumno_id else None
    
    return render_template('admin/notas.html',
                         notas=notas,
                         ciclos=ciclos,
                         cursos=cursos,
                         alumnos=alumnos,
                         ciclo_seleccionado=ciclo_seleccionado,
                         curso_seleccionado=curso_seleccionado,
                         alumno_seleccionado=alumno_seleccionado,
                         estado_seleccionado=estado)

@admin_bp.route('/notas/curso/<int:curso_id>')
@login_required
@admin_required
def ver_notas_curso(curso_id):
    """Ver notas de un curso específico"""
    curso = Curso.query.get_or_404(curso_id)
    
    # Obtener todas las notas del curso con alias para evitar conflicto de nombres
    from sqlalchemy.orm import aliased
    Alumno = aliased(Usuario)
    Docente = aliased(Usuario)
    
    notas = db.session.query(Nota, Alumno, Docente).join(
        Alumno, Nota.alumno_id == Alumno.id
    ).join(Docente, Nota.docente_id == Docente.id).filter(
        Nota.curso_id == curso_id
    ).order_by(Alumno.nombre, Alumno.apellido).all()
    
    # Obtener estadísticas del curso
    total_alumnos = CursoAlumno.query.filter_by(curso_id=curso_id).count()
    notas_publicadas = Nota.query.filter_by(curso_id=curso_id, estado='publicada').count()
    notas_borrador = Nota.query.filter_by(curso_id=curso_id, estado='borrador').count()
    
    # Calcular promedios
    notas_finales = [nota[0].nota_final for nota in notas if nota[0].nota_final > 0]
    promedio_curso = sum(notas_finales) / len(notas_finales) if notas_finales else 0
    
    return render_template('admin/notas_curso.html',
                         curso=curso,
                         notas=notas,
                         total_alumnos=total_alumnos,
                         notas_publicadas=notas_publicadas,
                         notas_borrador=notas_borrador,
                         promedio_curso=promedio_curso)

@admin_bp.route('/notas/alumno/<int:alumno_id>')
@login_required
@admin_required
def ver_notas_alumno(alumno_id):
    """Ver notas de un alumno específico"""
    alumno = Usuario.query.get_or_404(alumno_id)
    
    if alumno.rol != 'alumno':
        flash('El usuario no es un alumno.', 'error')
        return redirect(url_for('admin.ver_notas'))
    
    # Obtener todas las notas del alumno con alias para evitar conflicto de nombres
    from sqlalchemy.orm import aliased
    Docente = aliased(Usuario)
    
    notas = db.session.query(Nota, Curso, Docente).join(Curso).join(
        Docente, Nota.docente_id == Docente.id
    ).filter(Nota.alumno_id == alumno_id).order_by(Curso.nombre).all()
    
    # Obtener matrícula activa
    matricula_activa = MatriculaAlumno.query.filter_by(
        alumno_id=alumno_id, 
        estado='activa'
    ).first()
    
    # Calcular estadísticas del alumno
    notas_finales = [nota[0].nota_final for nota in notas if nota[0].nota_final > 0]
    promedio_general = sum(notas_finales) / len(notas_finales) if notas_finales else 0
    
    return render_template('admin/notas_alumno.html',
                         alumno=alumno,
                         notas=notas,
                         matricula_activa=matricula_activa,
                         promedio_general=promedio_general)

@admin_bp.route('/notas/exportar')
@login_required
@admin_required
def exportar_notas():
    """Exportar notas a CSV"""
    import csv
    import io
    from flask import Response
    from datetime import datetime
    
    # Obtener filtros
    ciclo_id = request.args.get('ciclo_id')
    curso_id = request.args.get('curso_id')
    estado = request.args.get('estado', 'todas')
    
    # Construir query con alias para evitar conflicto de nombres
    from sqlalchemy.orm import aliased
    Alumno = aliased(Usuario)
    Docente = aliased(Usuario)
    
    query = db.session.query(Nota, Curso, Alumno, Docente).join(Curso).join(
        Alumno, Nota.alumno_id == Alumno.id
    ).join(Docente, Nota.docente_id == Docente.id)
    
    if ciclo_id:
        query = query.filter(Curso.ciclo_academico_id == ciclo_id)
    if curso_id:
        query = query.filter(Nota.curso_id == curso_id)
    if estado != 'todas':
        query = query.filter(Nota.estado == estado)
    
    notas = query.order_by(Curso.nombre, Alumno.nombre).all()
    
    # Crear CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Escribir encabezados
    writer.writerow([
        'Curso', 'Código Curso', 'Alumno', 'DNI Alumno', 'Docente',
        'Parcial 1', 'Parcial 2', 'Parcial 3', 'Parcial 4',
        'Nota Final', 'Estado', 'Fecha Actualización', 'Comentarios'
    ])
    
    # Escribir datos
    for nota, curso, alumno, docente in notas:
        writer.writerow([
            curso.nombre,
            curso.codigo,
            f"{alumno.nombre} {alumno.apellido}",
            alumno.dni,
            f"{docente.nombre} {docente.apellido}",
            nota.parcial1,
            nota.parcial2,
            nota.parcial3,
            nota.parcial4,
            nota.nota_final,
            nota.estado,
            nota.fecha_actualizacion.strftime('%d/%m/%Y %H:%M') if nota.fecha_actualizacion else '',
            nota.comentarios or ''
        ])
    
    # Preparar respuesta
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=notas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        }
    )

# Gestión de Ciclos Académicos
@admin_bp.route('/ciclos')
@login_required
@admin_required
def ciclos():
    ciclos_data = []
    ciclos = CicloAcademico.query.order_by(CicloAcademico.orden).all()
    
    for ciclo in ciclos:
        # Verificar relaciones para cada ciclo
        cursos_asignados = Curso.query.filter_by(ciclo_academico_id=ciclo.id).count()
        matriculas = MatriculaAlumno.query.filter_by(ciclo_academico_id=ciclo.id).count()
        
        # Verificar notas en cursos del ciclo
        cursos_ciclo = Curso.query.filter_by(ciclo_academico_id=ciclo.id).all()
        notas_ciclo = 0
        for curso in cursos_ciclo:
            notas_ciclo += Nota.query.filter_by(curso_id=curso.id).count()
        
        # Determinar si se puede desactivar/eliminar
        puede_desactivar = cursos_asignados == 0 and matriculas == 0 and notas_ciclo == 0
        puede_eliminar = puede_desactivar
        
        ciclos_data.append({
            'ciclo': ciclo,
            'cursos_asignados': cursos_asignados,
            'matriculas': matriculas,
            'notas_ciclo': notas_ciclo,
            'puede_desactivar': puede_desactivar,
            'puede_eliminar': puede_eliminar
        })
    
    return render_template('admin/ciclos.html', ciclos=ciclos_data)

@admin_bp.route('/ciclos/registrar', methods=['GET', 'POST'])
@login_required
@admin_required
def registrar_ciclo():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        año = int(request.form.get('año'))
        ciclo = int(request.form.get('ciclo'))
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        ultimo_ciclo = CicloAcademico.query.order_by(CicloAcademico.orden.desc()).first()
        if ultimo_ciclo:
            orden = ultimo_ciclo.orden + 1
        else:
            orden = 1
        
        # Verificar que no exista un ciclo con el mismo orden
        if CicloAcademico.query.filter_by(orden=orden).first():
            flash('Ya existe un ciclo con ese orden.', 'error')
            return render_template('admin/registrar_ciclo.html')
        
        ciclo_academico = CicloAcademico(
            nombre=nombre,
            año=año,
            ciclo=ciclo,
            orden=orden,
            fecha_inicio=fecha_inicio if fecha_inicio else None,
            fecha_fin=fecha_fin if fecha_fin else None
        )
        
        try:
            db.session.add(ciclo_academico)
            db.session.commit()
            flash('Ciclo académico registrado correctamente.', 'success')
            return redirect(url_for('admin.ciclos'))
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar el ciclo académico.', 'error')
    
    return render_template('admin/registrar_ciclo.html')

# Matricular alumno en ciclo académico
@admin_bp.route('/matricular-ciclo', methods=['GET', 'POST'])
@login_required
@admin_required
def matricular_ciclo():
    if request.method == 'POST':
        alumno_id = request.form.get('alumno_id')
        ciclo_id = request.form.get('ciclo_id')
        forzar_matricula = request.form.get('forzar_matricula') == 'on'  # Checkbox para excepciones
        
        # Verificar que no esté ya matriculado en este ciclo
        if MatriculaAlumno.query.filter_by(alumno_id=alumno_id, ciclo_academico_id=ciclo_id).first():
            flash('Este alumno ya está matriculado en este ciclo.', 'error')
        else:
            # Verificar si ya está matriculado en otro ciclo activo
            matricula_activa = MatriculaAlumno.query.filter_by(
                alumno_id=alumno_id, 
                estado='activa'
            ).first()
            
            if matricula_activa and not forzar_matricula:
                ciclo_actual = matricula_activa.ciclo_academico
                flash(f'El alumno ya está matriculado en el ciclo "{ciclo_actual.nombre}". '
                      f'Si necesita matricularlo en otro ciclo (por ejemplo, por cursos jalados), '
                      f'marque la casilla "Forzar matrícula" y confirme.', 'warning')
                return render_template('admin/matricular_ciclo.html', 
                                     alumnos=Usuario.query.filter_by(rol='alumno', activo=True).all(),
                                     ciclos=CicloAcademico.query.filter_by(activo=True).order_by(CicloAcademico.orden).all(),
                                     matriculas=db.session.query(MatriculaAlumno, Usuario, CicloAcademico).join(Usuario).join(CicloAcademico).all(),
                                     alumno_seleccionado=alumno_id,
                                     ciclo_seleccionado=ciclo_id,
                                     mostrar_forzar=True)
            
            # Si hay matrícula activa y se está forzando, desactivar la anterior
            if matricula_activa and forzar_matricula:
                matricula_activa.estado = 'suspendida'
                flash(f'Matrícula anterior en "{matricula_activa.ciclo_academico.nombre}" suspendida.', 'info')
            
            # Crear nueva matrícula
            matricula = MatriculaAlumno(alumno_id=alumno_id, ciclo_academico_id=ciclo_id)
            db.session.add(matricula)
            
            # Matricular automáticamente en todos los cursos del ciclo
            ciclo = CicloAcademico.query.get(ciclo_id)
            cursos_ciclo = Curso.query.filter_by(ciclo_academico_id=ciclo_id).all()
            
            for curso in cursos_ciclo:
                # Verificar que no esté ya matriculado en el curso
                if not CursoAlumno.query.filter_by(curso_id=curso.id, alumno_id=alumno_id).first():
                    curso_alumno = CursoAlumno(curso_id=curso.id, alumno_id=alumno_id)
                    db.session.add(curso_alumno)
                    print(f"Matriculando {Usuario.query.get(alumno_id).nombre} en {curso.nombre}")  # Debug
            
            db.session.commit()
            flash(f'Alumno matriculado en el ciclo y {len(cursos_ciclo)} curso(s) automáticamente.', 'success')
        
        return redirect(url_for('admin.matricular_ciclo'))
    
    # Obtener alumnos con información de matrículas
    alumnos = db.session.query(Usuario).filter_by(rol='alumno', activo=True).all()
    
    # Agregar información de matrícula activa a cada alumno
    for alumno in alumnos:
        matricula_activa = MatriculaAlumno.query.filter_by(
            alumno_id=alumno.id, 
            estado='activa'
        ).first()
        alumno.matricula_activa = matricula_activa
    
    ciclos = CicloAcademico.query.filter_by(activo=True).order_by(CicloAcademico.orden).all()
    matriculas = db.session.query(MatriculaAlumno, Usuario, CicloAcademico).join(Usuario).join(CicloAcademico).all()
    
    return render_template('admin/matricular_ciclo.html', 
                         alumnos=alumnos, 
                         ciclos=ciclos, 
                         matriculas=matriculas)

# Funcionalidades adicionales para ciclos académicos
@admin_bp.route('/ciclos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_ciclo(id):
    ciclo = CicloAcademico.query.get_or_404(id)
    
    if request.method == 'POST':
        ciclo.nombre = request.form.get('nombre')
        ciclo.año = int(request.form.get('año'))
        ciclo.ciclo = int(request.form.get('ciclo'))
        ciclo.fecha_inicio = request.form.get('fecha_inicio') if request.form.get('fecha_inicio') else None
        ciclo.fecha_fin = request.form.get('fecha_fin') if request.form.get('fecha_fin') else None
        ciclo.activo = 'activo' in request.form
        ultimo_ciclo = CicloAcademico.query.order_by(CicloAcademico.orden.desc()).first()
        if ultimo_ciclo:
            orden = ultimo_ciclo.orden + 1
        else:
            orden = 1
        
        # Verificar que no exista otro ciclo con el mismo orden
        if CicloAcademico.query.filter(CicloAcademico.orden == ciclo.orden, CicloAcademico.id != id).first():
            flash('Ya existe un ciclo con ese orden.', 'error')
            return render_template('admin/editar_ciclo.html', ciclo=ciclo)
        
        try:
            db.session.commit()
            flash('Ciclo académico actualizado correctamente.', 'success')
            return redirect(url_for('admin.ciclos'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el ciclo académico.', 'error')
    
    return render_template('admin/editar_ciclo.html', ciclo=ciclo)
@admin_bp.route('/ciclos/toggle-activo/<int:id>', methods=['POST'])
@login_required
@admin_required
def toggle_activo_ciclo(id):
    ciclo = CicloAcademico.query.get_or_404(id)
    
    try:
        # Si se está desactivando, verificar relaciones
        if ciclo.activo:
            # Verificar si tiene cursos asignados
            cursos_asignados = Curso.query.filter_by(ciclo_academico_id=id).count()
            if cursos_asignados > 0:
                return jsonify({
                    'success': False, 
                    'message': f'No se puede desactivar el ciclo porque tiene {cursos_asignados} curso(s) asignado(s).'
                })
            
            # Verificar si tiene alumnos matriculados
            matriculas = MatriculaAlumno.query.filter_by(ciclo_academico_id=id).count()
            if matriculas > 0:
                return jsonify({
                    'success': False, 
                    'message': f'No se puede desactivar el ciclo porque tiene {matriculas} alumno(s) matriculado(s).'
                })
            
            # Verificar si tiene notas registradas en cursos del ciclo
            cursos_ciclo = Curso.query.filter_by(ciclo_academico_id=id).all()
            notas_ciclo = 0
            for curso in cursos_ciclo:
                notas_ciclo += Nota.query.filter_by(curso_id=curso.id).count()
            
            if notas_ciclo > 0:
                return jsonify({
                    'success': False, 
                    'message': f'No se puede desactivar el ciclo porque tiene {notas_ciclo} nota(s) registrada(s) en sus cursos.'
                })
        
        ciclo.activo = not ciclo.activo
        db.session.commit()
        
        estado = 'activado' if ciclo.activo else 'desactivado'
        return jsonify({
            'success': True, 
            'message': f'Ciclo {estado} correctamente.',
            'activo': ciclo.activo
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al cambiar el estado del ciclo.'})

@admin_bp.route('/ciclos/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_required
def eliminar_ciclo(id):
    ciclo = CicloAcademico.query.get_or_404(id)
    
    try:
        # Verificar si tiene cursos asignados
        cursos_asignados = Curso.query.filter_by(ciclo_academico_id=id).count()
        if cursos_asignados > 0:
            return jsonify({
                'success': False, 
                'message': f'No se puede eliminar el ciclo porque tiene {cursos_asignados} curso(s) asignado(s).'
            })
        
        # Verificar si tiene alumnos matriculados
        matriculas = MatriculaAlumno.query.filter_by(ciclo_academico_id=id).count()
        if matriculas > 0:
            return jsonify({
                'success': False, 
                'message': f'No se puede eliminar el ciclo porque tiene {matriculas} alumno(s) matriculado(s).'
            })
        
        # Verificar si tiene notas registradas en cursos del ciclo
        cursos_ciclo = Curso.query.filter_by(ciclo_academico_id=id).all()
        notas_ciclo = 0
        for curso in cursos_ciclo:
            notas_ciclo += Nota.query.filter_by(curso_id=curso.id).count()
        
        if notas_ciclo > 0:
            return jsonify({
                'success': False, 
                'message': f'No se puede eliminar el ciclo porque tiene {notas_ciclo} nota(s) registrada(s) en sus cursos.'
            })
        
        db.session.delete(ciclo)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Ciclo académico eliminado correctamente.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al eliminar el ciclo académico.'})

@admin_bp.route('/ciclos/duplicar/<int:id>', methods=['POST'])
@login_required
@admin_required
def duplicar_ciclo(id):
    ciclo_original = CicloAcademico.query.get_or_404(id)
    
    try:
        # Crear nuevo ciclo basado en el original
        nuevo_ciclo = CicloAcademico(
            nombre=f"{ciclo_original.nombre} (Copia)",
            año=ciclo_original.año,
            ciclo=ciclo_original.ciclo,
            orden=ciclo_original.orden + 1,  # Incrementar orden
            activo=True,
            fecha_inicio=ciclo_original.fecha_inicio,
            fecha_fin=ciclo_original.fecha_fin
        )
        
        db.session.add(nuevo_ciclo)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Ciclo académico duplicado correctamente.',
            'nuevo_id': nuevo_ciclo.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al duplicar el ciclo académico.'})

@admin_bp.route('/cursos/asignar-ciclo', methods=['GET', 'POST'])
@login_required
@admin_required
def asignar_ciclo_cursos():
    if request.method == 'POST':
        curso_id = request.form.get('curso_id')
        ciclo_id = request.form.get('ciclo_id')
        
        if not curso_id or not ciclo_id:
            flash('Selecciona un curso y un ciclo.', 'error')
            return redirect(url_for('admin.asignar_ciclo_cursos'))
        
        curso = Curso.query.get_or_404(curso_id)
        ciclo = CicloAcademico.query.get_or_404(ciclo_id)
        
        try:
            curso.ciclo_academico_id = ciclo_id
            db.session.commit()
            flash(f'Curso "{curso.nombre}" asignado al ciclo "{ciclo.nombre}" correctamente.', 'success')
            return redirect(url_for('admin.asignar_ciclo_cursos'))
        except Exception as e:
            db.session.rollback()
            flash('Error al asignar el ciclo al curso.', 'error')
    
    # Obtener cursos sin ciclo asignado
    cursos_sin_ciclo = Curso.query.filter(CicloAcademico.id.is_(None)).all()
    
    # Obtener todos los cursos con sus ciclos
    cursos_con_ciclo = db.session.query(Curso, CicloAcademico).outerjoin(CicloAcademico).all()
    
    # Obtener ciclos activos
    ciclos = CicloAcademico.query.filter_by(activo=True).order_by(CicloAcademico.orden).all()
    
    return render_template('admin/asignar_ciclo_cursos.html', 
                         cursos_sin_ciclo=cursos_sin_ciclo,
                         cursos_con_ciclo=cursos_con_ciclo,
                         ciclos=ciclos)

@admin_bp.route('/cursos/cambiar-ciclo/<int:curso_id>', methods=['POST'])
@login_required
@admin_required
def cambiar_ciclo_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    nuevo_ciclo_id = request.form.get('ciclo_id')
    
    if not nuevo_ciclo_id:
        return jsonify({'success': False, 'message': 'Selecciona un ciclo válido.'})
    
    try:
        ciclo_anterior = curso.ciclo_academico.nombre if curso.ciclo_academico else 'Sin ciclo'
        curso.ciclo_academico_id = nuevo_ciclo_id
        db.session.commit()
        
        nuevo_ciclo = CicloAcademico.query.get(nuevo_ciclo_id)
        return jsonify({
            'success': True, 
            'message': f'Curso movido de "{ciclo_anterior}" a "{nuevo_ciclo.nombre}" correctamente.'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al cambiar el ciclo del curso.'})

@admin_bp.route('/cursos/quitar-ciclo/<int:curso_id>', methods=['POST'])
@login_required
@admin_required
def quitar_ciclo_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    
    try:
        ciclo_anterior = curso.ciclo_academico.nombre if curso.ciclo_academico else 'Sin ciclo'
        curso.ciclo_academico_id = None
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Ciclo "{ciclo_anterior}" removido del curso correctamente.'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al quitar el ciclo del curso.'})

@admin_bp.route('/sincronizar-matriculas', methods=['POST'])
@login_required
@admin_required
def sincronizar_matriculas():
    """Sincroniza las matrículas de ciclos con las matrículas de cursos"""
    try:
        # Obtener todas las matrículas activas en ciclos
        matriculas_activas = MatriculaAlumno.query.filter_by(estado='activa').all()
        matriculas_creadas = 0
        
        for matricula in matriculas_activas:
            # Obtener cursos del ciclo
            cursos_ciclo = Curso.query.filter_by(ciclo_academico_id=matricula.ciclo_academico_id).all()
            
            for curso in cursos_ciclo:
                # Verificar si ya está matriculado en el curso
                if not CursoAlumno.query.filter_by(
                    curso_id=curso.id, 
                    alumno_id=matricula.alumno_id
                ).first():
                    # Crear matrícula en el curso
                    curso_alumno = CursoAlumno(
                        curso_id=curso.id,
                        alumno_id=matricula.alumno_id
                    )
                    db.session.add(curso_alumno)
                    matriculas_creadas += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Sincronización completada. Se crearon {matriculas_creadas} matrículas en cursos.'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error en la sincronización: {str(e)}'})
