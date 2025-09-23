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

class Nota(db.Model):
    __tablename__ = 'notas'
    
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    alumno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    docente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Notas parciales
    parcial1 = db.Column(db.Float, default=0.0)
    parcial2 = db.Column(db.Float, default=0.0)
    parcial3 = db.Column(db.Float, default=0.0)
    parcial4 = db.Column(db.Float, default=0.0)
    
    # Nota final
    nota_final = db.Column(db.Float, default=0.0)
    
    # Estado de la nota
    estado = db.Column(db.Enum('borrador', 'publicada'), default='borrador')
    
    # Fechas
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Comentarios
    comentarios = db.Column(db.Text)
    
    def calcular_nota_final(self):
        """Calcula la nota final basada en los parciales"""
        # Obtener el número de parciales del curso
        numero_parciales = self.curso.numero_parciales if hasattr(self.curso, 'numero_parciales') else 3
        
        # Recopilar notas válidas
        notas = []
        for i in range(1, min(numero_parciales + 1, 5)):  # máximo 4 parciales
            valor = getattr(self, f'parcial{i}', 0.0)
            if valor and valor > 0:
                notas.append(valor)
        
        # Calcular promedio
        if notas:
            self.nota_final = sum(notas) / len(notas)
        else:
            self.nota_final = 0.0
            
        return self.nota_final
    
    def __repr__(self):
        return f'<Nota {self.alumno.nombre} - {self.curso.nombre}: {self.nota_final}>'

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