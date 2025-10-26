"""
Sistema de Notas - Modelos de Datos
===================================
Este archivo define todos los modelos de datos (tablas) utilizados en el sistema.
Incluye definiciones para usuarios, cursos, notas, ciclos académicos y relaciones entre ellos.
"""

# Importaciones necesarias
from flask_sqlalchemy import SQLAlchemy  # ORM para interactuar con la base de datos
from flask_login import UserMixin        # Proporciona métodos para la autenticación de usuarios
from werkzeug.security import generate_password_hash, check_password_hash  # Seguridad para contraseñas
from datetime import datetime            # Manejo de fechas y horas
from app import db                       # Instancia de la base de datos

class Usuario(UserMixin, db.Model):
    """
    Modelo de Usuario: Representa a todos los usuarios del sistema (admin, docentes, alumnos)
    Hereda de UserMixin para funcionalidades de autenticación de Flask-Login
    """
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(20), unique=True, nullable=False)  # Documento de identidad único
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Contraseña encriptada
    rol = db.Column(db.Enum('admin', 'docente', 'alumno'), nullable=False)  # Tipo de usuario
    activo = db.Column(db.Boolean, default=True)  # Estado del usuario
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones con otras tablas
    cursos_asignados = db.relationship('CursoDocente', backref='docente', lazy=True)
    notas_como_alumno = db.relationship('Nota', foreign_keys='Nota.alumno_id', backref='alumno', lazy=True)
    notas_como_docente = db.relationship('Nota', foreign_keys='Nota.docente_id', backref='docente', lazy=True)
    
    def set_password(self, password):
        """Encripta y guarda la contraseña del usuario"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica si la contraseña proporcionada coincide con la almacenada"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.nombre} {self.apellido}>'

class Curso(db.Model):
    """
    Modelo de Curso: Representa las asignaturas o materias del sistema académico
    Almacena información básica del curso y sus relaciones con docentes, alumnos y notas
    """
    __tablename__ = 'cursos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)  # Nombre del curso
    codigo = db.Column(db.String(20), unique=True, nullable=False)  # Código único del curso
    descripcion = db.Column(db.Text)  # Descripción detallada del curso
    creditos = db.Column(db.Integer, default=3)  # Valor académico del curso
    numero_parciales = db.Column(db.Integer, default=3)  # Número de evaluaciones parciales
    ciclo_academico_id = db.Column(db.Integer, db.ForeignKey('ciclos_academicos.id'), nullable=True)  # Ciclo al que pertenece
    activo = db.Column(db.Boolean, default=True)  # Estado del curso
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones con otras tablas
    docentes = db.relationship('CursoDocente', backref='curso', lazy=True)  # Docentes asignados
    alumnos = db.relationship('CursoAlumno', backref='curso', lazy=True)  # Alumnos matriculados
    notas = db.relationship('Nota', backref='curso', lazy=True)  # Notas generales
    notas_actividades = db.relationship('NotaActividades', backref='curso', lazy=True)  # Notas de actividades
    notas_practicas = db.relationship('NotaPracticas', backref='curso', lazy=True)  # Notas de prácticas
    notas_parciales = db.relationship('NotaParcial', backref='curso', lazy=True)  # Notas de parciales
    
    def __repr__(self):
        return f'<Curso {self.nombre}>'

class CursoDocente(db.Model):
    """
    Modelo de relación entre Cursos y Docentes
    Establece qué docentes están asignados a cada curso
    """
    __tablename__ = 'curso_docente'
    
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)  # Referencia al curso
    docente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)  # Referencia al docente
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow)  # Fecha de asignación
    
    def __repr__(self):
        return f'<CursoDocente {self.curso.nombre} - {self.docente.nombre}>'

class CursoAlumno(db.Model):
    """
    Modelo de relación entre Cursos y Alumnos (matrícula)
    Establece qué alumnos están matriculados en cada curso
    """
    __tablename__ = 'curso_alumno'
    
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)  # Referencia al curso
    alumno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)  # Referencia al alumno
    fecha_matricula = db.Column(db.DateTime, default=datetime.utcnow)  # Fecha de matrícula
    
    def __repr__(self):
        return f'<CursoAlumno {self.curso.nombre} - {self.alumno.nombre}>'

# NUEVA TABLA: NotaActividades (8 notas + promedio)
class NotaActividades(db.Model):
    """
    Modelo para almacenar las notas de actividades de los alumnos
    Guarda hasta 8 notas de actividades y calcula su promedio
    """
    __tablename__ = 'notas_actividades'
    
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)  # Curso asociado
    alumno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)  # Alumno evaluado
    docente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)  # Docente evaluador
    
    # 8 notas de actividades individuales
    actividad1 = db.Column(db.Float, default=0.0)  # Primera actividad
    actividad2 = db.Column(db.Float, default=0.0)  # Segunda actividad
    actividad3 = db.Column(db.Float, default=0.0)  # Tercera actividad
    actividad4 = db.Column(db.Float, default=0.0)  # Cuarta actividad
    actividad5 = db.Column(db.Float, default=0.0)  # Quinta actividad
    actividad6 = db.Column(db.Float, default=0.0)  # Sexta actividad
    actividad7 = db.Column(db.Float, default=0.0)  # Séptima actividad
    actividad8 = db.Column(db.Float, default=0.0)  # Octava actividad
    
    # Promedio calculado de todas las actividades
    promedio_actividades = db.Column(db.Float, default=0.0)  # Promedio final
    
    # Estado y fechas
    estado = db.Column(db.Enum('borrador', 'publicada'), default='borrador')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    comentarios = db.Column(db.Text)
    
    # Relaciones
    alumno = db.relationship('Usuario', foreign_keys=[alumno_id], backref='notas_actividades_como_alumno', lazy=True)
    docente = db.relationship('Usuario', foreign_keys=[docente_id], backref='notas_actividades_como_docente', lazy=True)
    
    def calcular_promedio_actividades(self):
        """Calcula el promedio de las 8 actividades"""
        actividades = [
            self.actividad1, self.actividad2, self.actividad3, self.actividad4,
            self.actividad5, self.actividad6, self.actividad7, self.actividad8
        ]
        
        # Filtrar notas válidas (mayores a 0)
        notas_validas = [nota for nota in actividades if nota and nota > 0]
        
        if notas_validas:
            self.promedio_actividades = sum(notas_validas) / len(notas_validas)
        else:
            self.promedio_actividades = 0.0
            
        return self.promedio_actividades
    
    def __repr__(self):
        return f'<NotaActividades {self.alumno.nombre} - {self.curso.nombre}: {self.promedio_actividades}>'

# NUEVA TABLA: NotaPracticas (4 notas + promedio)
class NotaPracticas(db.Model):
    """
    Modelo para almacenar las notas de prácticas de los alumnos
    Guarda hasta 4 notas de prácticas y calcula su promedio
    """
    __tablename__ = 'notas_practicas'
    
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)  # Curso asociado
    alumno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)  # Alumno evaluado
    docente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)  # Docente evaluador
    
    # 4 notas de prácticas individuales
    practica1 = db.Column(db.Float, default=0.0)  # Primera práctica
    practica2 = db.Column(db.Float, default=0.0)  # Segunda práctica
    practica3 = db.Column(db.Float, default=0.0)  # Tercera práctica
    practica4 = db.Column(db.Float, default=0.0)  # Cuarta práctica
    
    # Promedio calculado de todas las prácticas
    promedio_practicas = db.Column(db.Float, default=0.0)  # Promedio final
    
    # Estado y fechas
    estado = db.Column(db.Enum('borrador', 'publicada'), default='borrador')  # Estado de publicación
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)  # Fecha de creación
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Fecha de última actualización
    comentarios = db.Column(db.Text)  # Comentarios adicionales
    
    # Relaciones con otras tablas
    alumno = db.relationship('Usuario', foreign_keys=[alumno_id], backref='notas_practicas_como_alumno', lazy=True)
    docente = db.relationship('Usuario', foreign_keys=[docente_id], backref='notas_practicas_como_docente', lazy=True)
    
    def calcular_promedio_practicas(self):
        """Calcula el promedio de las 4 prácticas"""
        practicas = [self.practica1, self.practica2, self.practica3, self.practica4]
        
        # Filtrar notas válidas (mayores a 0)
        notas_validas = [nota for nota in practicas if nota and nota > 0]
        
        if notas_validas:
            self.promedio_practicas = sum(notas_validas) / len(notas_validas)
        else:
            self.promedio_practicas = 0.0
            
        return self.promedio_practicas
    
    def __repr__(self):
        return f'<NotaPracticas {self.alumno.nombre} - {self.curso.nombre}: {self.promedio_practicas}>'

"""
Modelo NotaParcial: Almacena las notas de los exámenes parciales de los alumnos.

Este modelo gestiona las dos evaluaciones parciales principales del curso y calcula
su promedio. Cada nota parcial está asociada a un curso específico, un alumno y el
docente que la registra.
"""
class NotaParcial(db.Model):
    __tablename__ = 'notas_parciales'
    
    # Clave primaria y claves foráneas para relaciones
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)  # Curso al que pertenece la nota
    alumno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)  # Alumno evaluado
    docente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)  # Docente que registra la nota
    
    # Notas de los dos exámenes parciales del curso
    parcial1 = db.Column(db.Float, default=0.0)  # Nota del primer examen parcial
    parcial2 = db.Column(db.Float, default=0.0)  # Nota del segundo examen parcial
    
    # Promedio calculado de los parciales
    promedio_parciales = db.Column(db.Float, default=0.0)  # Promedio automático de los dos parciales
    
    # Metadatos de la nota
    estado = db.Column(db.Enum('borrador', 'publicada'), default='borrador')  # Estado de publicación de la nota
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)  # Fecha de registro inicial
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Última modificación
    comentarios = db.Column(db.Text)  # Observaciones o retroalimentación sobre las notas
    
    # Relaciones con otros modelos
    alumno = db.relationship('Usuario', foreign_keys=[alumno_id], backref='notas_parciales_como_alumno', lazy=True)  # Relación con el alumno
    docente = db.relationship('Usuario', foreign_keys=[docente_id], backref='notas_parciales_como_docente', lazy=True)  # Relación con el docente
    
    def calcular_promedio_parciales(self):
        """
        Calcula el promedio de los 2 exámenes parciales.
        
        Este método toma las notas de los dos parciales, filtra aquellas que son válidas
        (mayores a cero) y calcula su promedio. Si no hay notas válidas, establece
        el promedio en 0.0.
        
        Returns:
            float: El promedio calculado de los parciales.
        """
        # Crear lista con las notas de los dos parciales
        parciales = [self.parcial1, self.parcial2]
        
        # Filtrar notas válidas (mayores a 0)
        notas_validas = [nota for nota in parciales if nota and nota > 0]
        
        # Calcular el promedio si hay notas válidas
        if notas_validas:
            self.promedio_parciales = sum(notas_validas) / len(notas_validas)
        else:
            self.promedio_parciales = 0.0
            
        return self.promedio_parciales
    
    def __repr__(self):
        return f'<NotaParcial {self.alumno.nombre} - {self.curso.nombre}: {self.promedio_parciales}>'

"""
Modelo Nota: Representa la nota final de un alumno en un curso.

Este modelo integra los promedios de actividades, prácticas y parciales para calcular
la nota final del alumno. Funciona como un agregador de las diferentes evaluaciones
y aplica los pesos correspondientes para el cálculo del promedio final.
"""
class Nota(db.Model):
    __tablename__ = 'notas'
    
    # Clave primaria y claves foráneas para relaciones principales
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)  # Curso evaluado
    alumno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)  # Alumno evaluado
    docente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)  # Docente que registra
    
    # Referencias a las tablas de notas detalladas
    nota_actividades_id = db.Column(db.Integer, db.ForeignKey('notas_actividades.id'), nullable=True)  # Referencia a actividades
    nota_practicas_id = db.Column(db.Integer, db.ForeignKey('notas_practicas.id'), nullable=True)  # Referencia a prácticas
    nota_parcial_id = db.Column(db.Integer, db.ForeignKey('notas_parciales.id'), nullable=True)  # Referencia a parciales
    
    # Promedios de las 3 categorías de evaluación
    promedio_actividades = db.Column(db.Float, default=0.0)  # Promedio de actividades (10%)
    promedio_practicas = db.Column(db.Float, default=0.0)  # Promedio de prácticas (30%)
    promedio_parciales = db.Column(db.Float, default=0.0)  # Promedio de parciales (60%)
    
    # Nota final calculada con los pesos de cada categoría
    promedio_final = db.Column(db.Float, default=0.0)  # Promedio final ponderado
    
    # Metadatos de la nota
    estado = db.Column(db.Enum('borrador', 'publicada'), default='borrador')  # Estado de publicación
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)  # Fecha de registro inicial
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Última modificación
    comentarios = db.Column(db.Text)  # Observaciones o retroalimentación
    
    # Relaciones con las tablas de notas detalladas
    nota_actividades = db.relationship('NotaActividades', foreign_keys=[nota_actividades_id], lazy=True)  # Relación con actividades
    nota_practicas = db.relationship('NotaPracticas', foreign_keys=[nota_practicas_id], lazy=True)  # Relación con prácticas
    nota_parcial = db.relationship('NotaParcial', foreign_keys=[nota_parcial_id], lazy=True)  # Relación con parciales
    
    def calcular_promedio_final(self):
        """
        Calcula el promedio final basado en los promedios de actividades, prácticas y parciales.
        
        Este método obtiene los promedios de las tres categorías de evaluación, ya sea
        a través de referencias directas o buscando por curso y alumno. Luego aplica
        los pesos correspondientes (10% actividades, 30% prácticas, 60% parciales)
        para calcular la nota final del alumno.
        
        Returns:
            float: El promedio final ponderado.
        """
        # Si tenemos referencias directas, usar esas
        if self.nota_actividades_id and self.nota_actividades:
            self.promedio_actividades = self.nota_actividades.promedio_actividades or 0.0
        
        if self.nota_practicas_id and self.nota_practicas:
            self.promedio_practicas = self.nota_practicas.promedio_practicas or 0.0
            
        if self.nota_parcial_id and self.nota_parcial:
            self.promedio_parciales = self.nota_parcial.promedio_parciales or 0.0
        
        # Si no tenemos referencias, buscar por curso y alumno (fallback)
        if not self.nota_actividades_id:
            nota_actividades = NotaActividades.query.filter_by(
                curso_id=self.curso_id, 
                alumno_id=self.alumno_id
            ).first()
            self.promedio_actividades = nota_actividades.promedio_actividades if nota_actividades and nota_actividades.promedio_actividades else 0.0
        
        if not self.nota_practicas_id:
            nota_practicas = NotaPracticas.query.filter_by(
                curso_id=self.curso_id, 
                alumno_id=self.alumno_id
            ).first()
            self.promedio_practicas = nota_practicas.promedio_practicas if nota_practicas and nota_practicas.promedio_practicas else 0.0
        
        if not self.nota_parcial_id:
            nota_parcial = NotaParcial.query.filter_by(
                curso_id=self.curso_id, 
                alumno_id=self.alumno_id
            ).first()
            self.promedio_parciales = nota_parcial.promedio_parciales if nota_parcial and nota_parcial.promedio_parciales else 0.0
        
        # Asegurar que los promedios no sean None
        self.promedio_actividades = self.promedio_actividades or 0.0
        self.promedio_practicas = self.promedio_practicas or 0.0
        self.promedio_parciales = self.promedio_parciales or 0.0
        
        # Calcular promedio final con los pesos definidos
        peso_actividades = 0.10  # 10% del peso total
        peso_practicas = 0.30    # 30% del peso total
        peso_parciales = 0.60    # 60% del peso total
        
        self.promedio_final = (
            (self.promedio_actividades * peso_actividades) +
            (self.promedio_practicas * peso_practicas) +
            (self.promedio_parciales * peso_parciales)
        )
            
        return self.promedio_final
    
    def __repr__(self):
        return f'<Nota {self.alumno.nombre} - {self.curso.nombre}: {self.promedio_final}>'

"""
Modelo CicloAcademico: Representa un periodo académico en la institución.

Este modelo gestiona los ciclos académicos del sistema, permitiendo organizar
los cursos por año y ciclo. Cada ciclo tiene un orden secuencial y fechas
de inicio y fin que determinan su periodo de vigencia.
"""
class CicloAcademico(db.Model):
    __tablename__ = 'ciclos_academicos'
    
    # Atributos principales
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)  # Nombre descriptivo del ciclo (ej: "Primer Año - Ciclo I")
    año = db.Column(db.Integer, nullable=False)  # Año académico (1, 2, 3, etc.)
    ciclo = db.Column(db.Integer, nullable=False)  # Número de ciclo dentro del año (1, 2)
    orden = db.Column(db.Integer, nullable=False)  # Orden secuencial global (1, 2, 3, 4, 5, 6)
    activo = db.Column(db.Boolean, default=True)  # Indica si el ciclo está actualmente activo
    fecha_inicio = db.Column(db.Date)  # Fecha de inicio del ciclo académico
    fecha_fin = db.Column(db.Date)  # Fecha de finalización del ciclo académico
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)  # Fecha de registro en el sistema
    
    # Relaciones con otros modelos
    cursos = db.relationship('Curso', backref='ciclo_academico', lazy=True)  # Cursos asociados a este ciclo
    matriculas = db.relationship('MatriculaAlumno', backref='ciclo_academico', lazy=True)  # Matrículas de este ciclo
    
    def __repr__(self):
        return f'<CicloAcademico {self.nombre}>'

"""
Modelo MatriculaAlumno: Registra la matrícula de un alumno en un ciclo académico.

Este modelo gestiona la relación entre alumnos y ciclos académicos, permitiendo
registrar cuándo un alumno se matricula en un ciclo específico y el estado
actual de dicha matrícula.
"""
class MatriculaAlumno(db.Model):
    __tablename__ = 'matriculas_alumnos'
    
    # Atributos principales
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)  # Alumno matriculado
    ciclo_academico_id = db.Column(db.Integer, db.ForeignKey('ciclos_academicos.id'), nullable=False)  # Ciclo de matrícula
    fecha_matricula = db.Column(db.DateTime, default=datetime.utcnow)  # Fecha en que se realizó la matrícula
    estado = db.Column(db.Enum('activa', 'completada', 'suspendida'), default='activa')  # Estado actual de la matrícula
    
    # Relaciones con otros modelos
    alumno = db.relationship('Usuario', backref='matriculas', lazy=True)  # Relación con el alumno
    
    def __repr__(self):
        return f'<MatriculaAlumno {self.alumno.nombre} - {self.ciclo_academico.nombre}>'

"""
Modelo ThemeConfig: Gestiona la configuración visual del sistema.

Este modelo almacena los colores y estilos visuales de la aplicación,
permitiendo personalizar la apariencia del sistema mediante la definición
de una paleta de colores coherente.
"""
class ThemeConfig(db.Model):
    __tablename__ = 'theme_config'

    # Atributos de configuración visual
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), default='Default')  # Nombre del tema
    color_oscuro = db.Column(db.String(7), default='#00378F')  # Color principal oscuro (formato hexadecimal)
    color_claro = db.Column(db.String(7), default='#3775DA')  # Color principal claro
    color_medio = db.Column(db.String(7), default='#1C56B5')  # Color intermedio
    color_medio_oscuro = db.Column(db.String(7), default='#0E47A2')  # Variante oscura del color intermedio
    color_medio_claro = db.Column(db.String(7), default='#2966C7')  # Variante clara del color intermedio
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Fecha de última actualización

    def __repr__(self):
        return f'<ThemeConfig {self.nombre}>'