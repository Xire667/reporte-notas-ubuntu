#!/usr/bin/env python3
"""
Script de inicialización de la base de datos
Ejecutar este script para crear las tablas y datos iniciales
"""

from app import create_app, db
from app.models import Usuario, Curso, CursoDocente, CursoAlumno, Nota

def init_database():
    """Inicializa la base de datos con tablas y datos de ejemplo"""
    app = create_app()
    
    with app.app_context():
        # Crear todas las tablas
        print("Creando tablas de la base de datos...")
        db.create_all()
        print("✅ Tablas creadas exitosamente")
        
        # Verificar si ya existen usuarios
        if Usuario.query.first():
            print("⚠️  La base de datos ya contiene datos. Saltando creación de datos de ejemplo.")
            return
        
        # Crear usuario administrador por defecto
        print("Creando usuario administrador por defecto...")
        admin = Usuario(
            dni='12345678',
            nombre='Administrador',
            apellido='Sistema',
            email='admin@sistema.edu',
            rol='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Crear algunos cursos de ejemplo
        print("Creando cursos de ejemplo...")
        cursos_ejemplo = [
            {
                'nombre': 'Programación Web I',
                'codigo': 'PROG101',
                'descripcion': 'Fundamentos de programación web con HTML, CSS y JavaScript',
                'creditos': 4
            },
            {
                'nombre': 'Base de Datos',
                'codigo': 'BD101',
                'descripcion': 'Diseño y gestión de bases de datos relacionales',
                'creditos': 3
            },
            {
                'nombre': 'Desarrollo de Aplicaciones',
                'codigo': 'APP201',
                'descripcion': 'Desarrollo de aplicaciones web con Flask y Python',
                'creditos': 5
            }
        ]
        
        for curso_data in cursos_ejemplo:
            curso = Curso(**curso_data)
            db.session.add(curso)
        
        # Crear docente de ejemplo
        print("Creando docente de ejemplo...")
        docente = Usuario(
            dni='87654321',
            nombre='Juan',
            apellido='Pérez',
            email='juan.perez@sistema.edu',
            rol='docente'
        )
        docente.set_password('docente123')
        db.session.add(docente)
        
        # Crear alumno de ejemplo
        print("Creando alumno de ejemplo...")
        alumno = Usuario(
            dni='11223344',
            nombre='María',
            apellido='González',
            email='maria.gonzalez@sistema.edu',
            rol='alumno'
        )
        alumno.set_password('alumno123')
        db.session.add(alumno)
        
        # Guardar cambios
        db.session.commit()
        print("✅ Datos de ejemplo creados exitosamente")
        
        # Asignar cursos al docente
        print("Asignando cursos al docente...")
        cursos = Curso.query.all()
        docente = Usuario.query.filter_by(rol='docente').first()
        
        for curso in cursos:
            asignacion = CursoDocente(curso_id=curso.id, docente_id=docente.id)
            db.session.add(asignacion)
        
        # Matricular alumno en cursos
        print("Matriculando alumno en cursos...")
        alumno = Usuario.query.filter_by(rol='alumno').first()
        
        for curso in cursos:
            matricula = CursoAlumno(curso_id=curso.id, alumno_id=alumno.id)
            db.session.add(matricula)
        
        db.session.commit()
        print("✅ Asignaciones y matrículas creadas exitosamente")
        
        # Crear algunas notas de ejemplo
        print("Creando notas de ejemplo...")
        for curso in cursos:
            nota = Nota(
                curso_id=curso.id,
                alumno_id=alumno.id,
                docente_id=docente.id,
                parcial1=15.5,
                parcial2=18.0,
                parcial3=16.5,
                estado='publicada'
            )
            nota.calcular_nota_final()
            db.session.add(nota)
        
        db.session.commit()
        print("✅ Notas de ejemplo creadas exitosamente")
        
        print("\n" + "="*50)
        print("🎉 INICIALIZACIÓN COMPLETADA")
        print("="*50)
        print("\nUsuarios creados:")
        print("👨‍💼 Administrador:")
        print("   DNI: 12345678")
        print("   Contraseña: admin123")
        print("\n👨‍🏫 Docente:")
        print("   DNI: 87654321")
        print("   Contraseña: docente123")
        print("\n👨‍🎓 Alumno:")
        print("   DNI: 11223344")
        print("   Contraseña: alumno123")
        print("\n🌐 Accede a la aplicación en: http://localhost:5000")
        print("="*50)

if __name__ == '__main__':
    init_database()
