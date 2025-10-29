#!/usr/bin/env python3
"""
Script de inicialización de la base de datos
Ejecutar este script para crear las tablas y datos iniciales
"""

from app import create_app, db
from app.models import Usuario

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
        print("✅ Usuarios creados exitosamente")
        

        

        
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
