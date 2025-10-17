from flask import render_template, request, redirect, url_for, flash, jsonify, make_response, abort
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
            flash('No tienes permisos para acceder a esta pÃ¡gina.', 'error')
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
    """Redirige a la vista de alumnos del curso para seleccionar el alumno especÃ­fico"""
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
        
        # Verificar que el alumno estÃ© matriculado en el curso
        matricula = CursoAlumno.query.filter_by(
            curso_id=curso_id,
            alumno_id=alumno_id
        ).first()
        
        if not matricula:
            return jsonify({'success': False, 'message': 'El alumno no estÃ¡ matriculado en este curso.'})
        
        # Recopilar y validar notas de actividades (8 actividades)
        actividades = {}
        for i in range(1, 9):
            valor = request.form.get(f'actividad{i}')
            try:
                actividades[f'actividad{i}'] = float(valor) if valor and valor.strip() != '' else 0.0
            except ValueError:
                return jsonify({'success': False, 'message': f'Error en el formato de la actividad {i}. Debe ser un nÃºmero vÃ¡lido.'})
        
        # Recopilar y validar notas de prÃ¡cticas (4 prÃ¡cticas)
        practicas = {}
        for i in range(1, 5):
            valor = request.form.get(f'practica{i}')
            try:
                practicas[f'practica{i}'] = float(valor) if valor and valor.strip() != '' else 0.0
            except ValueError:
                return jsonify({'success': False, 'message': f'Error en el formato de la prÃ¡ctica {i}. Debe ser un nÃºmero vÃ¡lido.'})
        
        # Recopilar y validar notas de parciales (2 parciales)
        parciales = {}
        for i in range(1, 3):
            valor = request.form.get(f'parcial{i}')
            try:
                parciales[f'parcial{i}'] = float(valor) if valor and valor.strip() != '' else 0.0
            except ValueError:
                return jsonify({'success': False, 'message': f'Error en el formato del parcial {i}. Debe ser un nÃºmero vÃ¡lido.'})
        
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
        
        # Actualizar prÃ¡cticas
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
            return jsonify({'success': False, 'message': 'No se encontrÃ³ la nota.'})
        
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

@docente_bp.route('/reportes')
@login_required
@docente_required
def reportes():
    cursos = db.session.query(Curso).join(CursoDocente).filter(
        CursoDocente.docente_id == current_user.id
    ).order_by(Curso.nombre).all()

    alumnos = db.session.query(Usuario).join(CursoAlumno).join(Curso).join(CursoDocente).filter(
        CursoDocente.docente_id == current_user.id,
        Usuario.rol == 'alumno'
    ).order_by(Usuario.nombre).all()

    alumnos_unicos = []
    vistos = set()
    for a in alumnos:
        if a.id not in vistos:
            alumnos_unicos.append(a)
            vistos.add(a.id)

    return render_template('docente/reportes.html', cursos=cursos, alumnos=alumnos_unicos)

@docente_bp.route('/reportes/curso/<int:curso_id>')
@login_required
@docente_required
def reporte_curso(curso_id):
    from datetime import datetime
    # Seguridad y contexto del docente si aplica
    try:
        curso = Curso.query.get_or_404(curso_id)
    except Exception:
        abort(404)

    # Obtener alumnos del curso (modelo Usuario, rol alumno)
    alumnos = db.session.query(Usuario).join(CursoAlumno).filter(
        CursoAlumno.curso_id == curso_id,
        Usuario.rol == 'alumno'
    ).order_by(Usuario.apellido.asc(), Usuario.nombre.asc()).all()
    datos = []

    for alumno in alumnos:
        na = NotaActividades.query.filter_by(curso_id=curso_id, alumno_id=alumno.id).first()
        np = NotaPracticas.query.filter_by(curso_id=curso_id, alumno_id=alumno.id).first()
        npa = NotaParcial.query.filter_by(curso_id=curso_id, alumno_id=alumno.id).first()
        nota = Nota.query.filter_by(curso_id=curso_id, alumno_id=alumno.id).first()

        actividades = []
        if na:
            actividades = [na.actividad1, na.actividad2, na.actividad3, na.actividad4, na.actividad5, na.actividad6, na.actividad7, na.actividad8]
        else:
            actividades = []

        practicas = []
        if np:
            practicas = [np.practica1, np.practica2, np.practica3, np.practica4]
        else:
            practicas = []

        parciales = []
        if npa:
            parciales = [npa.parcial1, npa.parcial2]
        else:
            parciales = []

        prom_acts = 0.0
        prom_pracs = 0.0
        prom_parcs = 0.0

        if nota:
            prom_acts = getattr(nota, 'promedio_actividades', 0.0) or 0.0
            prom_pracs = getattr(nota, 'promedio_practicas', 0.0) or 0.0
            prom_parcs = getattr(nota, 'promedio_parciales', 0.0) or 0.0
        
        # Si promedios están en cero, intenta calcular desde tablas de detalle
        if prom_acts == 0.0 and na:
            prom_acts = getattr(na, 'promedio_actividades', 0.0) or 0.0
        if prom_pracs == 0.0 and np:
            prom_pracs = getattr(np, 'promedio_practicas', 0.0) or 0.0
        if prom_parcs == 0.0 and npa:
            prom_parcs = getattr(npa, 'promedio_parciales', 0.0) or 0.0

        promedio_final = round((prom_acts * 0.10) + (prom_pracs * 0.30) + (prom_parcs * 0.60), 2)
        estado = getattr(nota, 'estado', None) if nota else None

        datos.append({
            'alumno': alumno,
            'actividades': actividades,
            'practicas': practicas,
            'parciales': parciales,
            'promedio_actividades': round(prom_acts, 2) if prom_acts is not None else None,
            'promedio_practicas': round(prom_pracs, 2) if prom_pracs is not None else None,
            'promedio_parciales': round(prom_parcs, 2) if prom_parcs is not None else None,
            'promedio_final': promedio_final,
            'estado': estado
        })

    return render_template('docente/reporte_curso.html', curso=curso, datos=datos)

@docente_bp.route('/reportes/alumno/<int:alumno_id>')
@login_required
@docente_required
def reporte_alumno(alumno_id):
    alumno = Usuario.query.get_or_404(alumno_id)

    cursos = db.session.query(Curso).join(CursoDocente).join(CursoAlumno, CursoAlumno.curso_id == Curso.id).filter(
        CursoDocente.docente_id == current_user.id,
        CursoAlumno.alumno_id == alumno_id
    ).order_by(Curso.nombre).all()

    datos = []
    for curso in cursos:
        nota = Nota.query.filter_by(curso_id=curso.id, alumno_id=alumno_id).first()
        prom_acts = 0.0
        prom_pracs = 0.0
        prom_parcs = 0.0
        prom_final = 0.0
        estado = None

        if nota:
            prom_acts = nota.promedio_actividades or 0.0
            prom_pracs = nota.promedio_practicas or 0.0
            prom_parcs = nota.promedio_parciales or 0.0
            estado = nota.estado

            if prom_acts == 0:
                na = NotaActividades.query.filter_by(curso_id=curso.id, alumno_id=alumno_id).first()
                prom_acts = na.promedio_actividades if na and na.promedio_actividades else 0.0
            if prom_pracs == 0:
                np = NotaPracticas.query.filter_by(curso_id=curso.id, alumno_id=alumno_id).first()
                prom_pracs = np.promedio_practicas if np and np.promedio_practicas else 0.0
            if prom_parcs == 0:
                npa = NotaParcial.query.filter_by(curso_id=curso.id, alumno_id=alumno_id).first()
                prom_parcs = npa.promedio_parciales if npa and npa.promedio_parciales else 0.0

            prom_final = (prom_acts * 0.10) + (prom_pracs * 0.30) + (prom_parcs * 0.60)
        else:
            na = NotaActividades.query.filter_by(curso_id=curso.id, alumno_id=alumno_id).first()
            np = NotaPracticas.query.filter_by(curso_id=curso.id, alumno_id=alumno_id).first()
            npa = NotaParcial.query.filter_by(curso_id=curso.id, alumno_id=alumno_id).first()
            prom_acts = na.promedio_actividades if na and na.promedio_actividades else 0.0
            prom_pracs = np.promedio_practicas if np and np.promedio_practicas else 0.0
            prom_parcs = npa.promedio_parciales if npa and npa.promedio_parciales else 0.0
            prom_final = (prom_acts * 0.10) + (prom_pracs * 0.30) + (prom_parcs * 0.60)

        datos.append({
            'curso': curso,
            'promedio_actividades': prom_acts,
            'promedio_practicas': prom_pracs,
            'promedio_parciales': prom_parcs,
            'promedio_final': prom_final,
            'estado': estado
        })

    return render_template('docente/reporte_alumno.html', alumno=alumno, datos=datos)


@docente_bp.route('/reportes/curso/<int:curso_id>/pdf')
@login_required
@docente_required
def reporte_curso_pdf(curso_id):
    # Construir los mismos datos detallados que en la vista HTML
    try:
        curso = Curso.query.get_or_404(curso_id)
    except Exception:
        abort(404)

    # Obtener alumnos del curso (modelo Usuario, rol alumno)
    alumnos = db.session.query(Usuario).join(CursoAlumno).filter(
        CursoAlumno.curso_id == curso_id,
        Usuario.rol == 'alumno'
    ).order_by(Usuario.apellido.asc(), Usuario.nombre.asc()).all()
    datos = []
    for alumno in alumnos:
        na = NotaActividades.query.filter_by(curso_id=curso_id, alumno_id=alumno.id).first()
        np = NotaPracticas.query.filter_by(curso_id=curso_id, alumno_id=alumno.id).first()
        npa = NotaParcial.query.filter_by(curso_id=curso_id, alumno_id=alumno.id).first()
        nota = Nota.query.filter_by(curso_id=curso_id, alumno_id=alumno.id).first()

        actividades = [na.actividad1, na.actividad2, na.actividad3, na.actividad4, na.actividad5, na.actividad6, na.actividad7, na.actividad8] if na else []
        practicas = [np.practica1, np.practica2, np.practica3, np.practica4] if np else []
        parciales = [npa.parcial1, npa.parcial2] if npa else []

        prom_acts = 0.0
        prom_pracs = 0.0
        prom_parcs = 0.0
        if nota:
            prom_acts = getattr(nota, 'promedio_actividades', 0.0) or 0.0
            prom_pracs = getattr(nota, 'promedio_practicas', 0.0) or 0.0
            prom_parcs = getattr(nota, 'promedio_parciales', 0.0) or 0.0
        if prom_acts == 0.0 and na:
            prom_acts = getattr(na, 'promedio_actividades', 0.0) or 0.0
        if prom_pracs == 0.0 and np:
            prom_pracs = getattr(np, 'promedio_practicas', 0.0) or 0.0
        if prom_parcs == 0.0 and npa:
            prom_parcs = getattr(npa, 'promedio_parciales', 0.0) or 0.0

        promedio_final = round((prom_acts * 0.10) + (prom_pracs * 0.30) + (prom_parcs * 0.60), 2)
        estado = getattr(nota, 'estado', None) if nota else None

        datos.append({
            'alumno': alumno,
            'actividades': actividades,
            'practicas': practicas,
            'parciales': parciales,
            'promedio_actividades': round(prom_acts, 2) if prom_acts is not None else None,
            'promedio_practicas': round(prom_pracs, 2) if prom_pracs is not None else None,
            'promedio_parciales': round(prom_parcs, 2) if prom_parcs is not None else None,
            'promedio_final': promedio_final,
            'estado': estado
        })

    html = render_template('docente/reporte_curso_pdf.html', curso=curso, datos=datos)
    from xhtml2pdf import pisa
    from io import BytesIO
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if hasattr(pisa_status, 'err') and pisa_status.err:
        flash('Error generando PDF.', 'error')
        return redirect(url_for('docente.reporte_curso', curso_id=curso_id))

    response = make_response(result.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f"attachment; filename=reporte_curso_{curso.codigo}.pdf"
    return response

