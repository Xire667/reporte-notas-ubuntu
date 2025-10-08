from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('admin', 'docente', 'alumno'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    cursos_asignados = db.relationship('CursoDocente', backref='docente', lazy=True)
    notas_como_alumno = db.relationship('Nota', foreign_keys='Nota.alumno_id', backref='alumno', lazy=True)
    notas_como_docente = db.relationship('Nota', foreign_keys='Nota.docente_id', backref='docente', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.nombre} {self.apellido}>'

class Curso(db.Model):
    __tablename__ = 'cursos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    creditos = db.Column(db.Integer, default=3)
    numero_parciales = db.Column(db.Integer, default=3)  # Número de parciales para este curso
    ciclo_academico_id = db.Column(db.Integer, db.ForeignKey('ciclos_academicos.id'), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    docentes = db.relationship('CursoDocente', backref='curso', lazy=True)
    alumnos = db.relationship('CursoAlumno', backref='curso', lazy=True)
    notas = db.relationship('Nota', backref='curso', lazy=True)
    notas_actividades = db.relationship('NotaActividades', backref='curso', lazy=True)
    notas_practicas = db.relationship('NotaPracticas', backref='curso', lazy=True)
    notas_parciales = db.relationship('NotaParcial', backref='curso', lazy=True)
    
    def __repr__(self):
        return f'<Curso {self.nombre}>'

class CursoDocente(db.Model):
    __tablename__ = 'curso_docente'
    
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    docente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CursoDocente {self.curso.nombre} - {self.docente.nombre}>'

class CursoAlumno(db.Model):
    __tablename__ = 'curso_alumno'
    
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    alumno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_matricula = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CursoAlumno {self.curso.nombre} - {self.alumno.nombre}>'

# NUEVA TABLA: NotaActividades (8 notas + promedio)
class NotaActividades(db.Model):
    __tablename__ = 'notas_actividades'
    
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    alumno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    docente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # 8 notas de actividades
    actividad1 = db.Column(db.Float, default=0.0)
    actividad2 = db.Column(db.Float, default=0.0)
    actividad3 = db.Column(db.Float, default=0.0)
    actividad4 = db.Column(db.Float, default=0.0)
    actividad5 = db.Column(db.Float, default=0.0)
    actividad6 = db.Column(db.Float, default=0.0)
    actividad7 = db.Column(db.Float, default=0.0)
    actividad8 = db.Column(db.Float, default=0.0)
    
    # Promedio de actividades
    promedio_actividades = db.Column(db.Float, default=0.0)
    
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
    __tablename__ = 'notas_practicas'
    
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    alumno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    docente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # 4 notas de prácticas
    practica1 = db.Column(db.Float, default=0.0)
    practica2 = db.Column(db.Float, default=0.0)
    practica3 = db.Column(db.Float, default=0.0)
    practica4 = db.Column(db.Float, default=0.0)
    
    # Promedio de prácticas
    promedio_practicas = db.Column(db.Float, default=0.0)
    
    # Estado y fechas
    estado = db.Column(db.Enum('borrador', 'publicada'), default='borrador')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    comentarios = db.Column(db.Text)
    
    # Relaciones
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

# NUEVA TABLA: NotaParcial (2 notas + promedio)
class NotaParcial(db.Model):
    __tablename__ = 'notas_parciales'
    
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    alumno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    docente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # 2 notas parciales
    parcial1 = db.Column(db.Float, default=0.0)
    parcial2 = db.Column(db.Float, default=0.0)
    
    # Promedio de parciales
    promedio_parciales = db.Column(db.Float, default=0.0)
    
    # Estado y fechas
    estado = db.Column(db.Enum('borrador', 'publicada'), default='borrador')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    comentarios = db.Column(db.Text)
    
    # Relaciones
    alumno = db.relationship('Usuario', foreign_keys=[alumno_id], backref='notas_parciales_como_alumno', lazy=True)
    docente = db.relationship('Usuario', foreign_keys=[docente_id], backref='notas_parciales_como_docente', lazy=True)
    
    def calcular_promedio_parciales(self):
        """Calcula el promedio de los 2 parciales"""
        parciales = [self.parcial1, self.parcial2]
        
        # Filtrar notas válidas (mayores a 0)
        notas_validas = [nota for nota in parciales if nota and nota > 0]
        
        if notas_validas:
            self.promedio_parciales = sum(notas_validas) / len(notas_validas)
        else:
            self.promedio_parciales = 0.0
            
        return self.promedio_parciales
    
    def __repr__(self):
        return f'<NotaParcial {self.alumno.nombre} - {self.curso.nombre}: {self.promedio_parciales}>'

# TABLA MODIFICADA: Nota (ahora con promedios de las 3 nuevas tablas)
class Nota(db.Model):
    __tablename__ = 'notas'
    
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    alumno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    docente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Referencias a las tablas de notas detalladas
    nota_actividades_id = db.Column(db.Integer, db.ForeignKey('notas_actividades.id'), nullable=True)
    nota_practicas_id = db.Column(db.Integer, db.ForeignKey('notas_practicas.id'), nullable=True)
    nota_parcial_id = db.Column(db.Integer, db.ForeignKey('notas_parciales.id'), nullable=True)
    
    # Promedios de las 3 nuevas tablas
    promedio_actividades = db.Column(db.Float, default=0.0)
    promedio_practicas = db.Column(db.Float, default=0.0)
    promedio_parciales = db.Column(db.Float, default=0.0)
    
    # Promedio final
    promedio_final = db.Column(db.Float, default=0.0)
    
    # Estado de la nota
    estado = db.Column(db.Enum('borrador', 'publicada'), default='borrador')
    
    # Fechas
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Comentarios
    comentarios = db.Column(db.Text)
    
    # Relaciones con las tablas de notas detalladas
    nota_actividades = db.relationship('NotaActividades', foreign_keys=[nota_actividades_id], lazy=True)
    nota_practicas = db.relationship('NotaPracticas', foreign_keys=[nota_practicas_id], lazy=True)
    nota_parcial = db.relationship('NotaParcial', foreign_keys=[nota_parcial_id], lazy=True)
    
    def calcular_promedio_final(self):
        """Calcula el promedio final basado en los 3 promedios"""
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
        
        # Calcular promedio final (puedes ajustar los pesos según necesites)
        # Ejemplo: 30% actividades, 30% prácticas, 40% parciales
        peso_actividades = 0.10
        peso_practicas = 0.30
        peso_parciales = 0.60
        
        self.promedio_final = (
            (self.promedio_actividades * peso_actividades) +
            (self.promedio_practicas * peso_practicas) +
            (self.promedio_parciales * peso_parciales)
        )
            
        return self.promedio_final
    
    def __repr__(self):
        return f'<Nota {self.alumno.nombre} - {self.curso.nombre}: {self.promedio_final}>'

class CicloAcademico(db.Model):
    __tablename__ = 'ciclos_academicos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)  # Ej: "Primer Año - Ciclo I"
    año = db.Column(db.Integer, nullable=False)  # 1, 2, 3
    ciclo = db.Column(db.Integer, nullable=False)  # 1, 2
    orden = db.Column(db.Integer, nullable=False)  # Orden secuencial: 1, 2, 3, 4, 5, 6
    activo = db.Column(db.Boolean, default=True)
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    cursos = db.relationship('Curso', backref='ciclo_academico', lazy=True)
    matriculas = db.relationship('MatriculaAlumno', backref='ciclo_academico', lazy=True)
    
    def __repr__(self):
        return f'<CicloAcademico {self.nombre}>'

class MatriculaAlumno(db.Model):
    __tablename__ = 'matriculas_alumnos'
    
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    ciclo_academico_id = db.Column(db.Integer, db.ForeignKey('ciclos_academicos.id'), nullable=False)
    fecha_matricula = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.Enum('activa', 'completada', 'suspendida'), default='activa')
    
    # Relaciones
    alumno = db.relationship('Usuario', backref='matriculas', lazy=True)
    
    def __repr__(self):
        return f'<MatriculaAlumno {self.alumno.nombre} - {self.ciclo_academico.nombre}>'