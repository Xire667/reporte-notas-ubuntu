#!/usr/bin/env python3
"""
Script para limpiar la base de datos
Ejecutar este script para eliminar todas las tablas y datos
"""

from app import create_app, db

def clean_database():
    """Elimina todas las tablas de la base de datos"""
    app = create_app()
    
    with app.app_context():
        print("Eliminando todas las tablas de la base de datos...")
        db.drop_all()
        print("✅ Todas las tablas han sido eliminadas")
        
        print("Creando tablas nuevamente...")
        db.create_all()
        print("✅ Tablas creadas exitosamente")
        
        print("\n🎉 Base de datos limpia y lista para usar")
        print("Ahora puedes ejecutar 'python init_db.py' para crear datos de ejemplo")

if __name__ == '__main__':
    clean_database()