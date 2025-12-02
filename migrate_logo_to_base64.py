"""
Script de migración: Convierte logos de archivos a base64 en BD
Ejecutar una sola vez después de actualizar el código
"""

import os
import sys
import base64
from app import create_app, db
from app.models import ThemeConfig


def migrate_logo_to_base64():
    """Migra logos existentes de archivos a base64"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("MIGRACIÓN: Logo de archivo a base64")
        print("=" * 60)
        
        # Obtener configuración actual
        config = ThemeConfig.query.first()
        
        if not config:
            print("\n❌ No hay configuración de tema en la base de datos")
            print("No es necesario migrar")
            return
        
        print(f"\n📋 Configuración encontrada: {config.nombre}")
        print(f"Logo actual: {config.logo_url or 'Sin logo'}")
        
        # Verificar si ya es base64
        if config.logo_url and config.logo_url.startswith('data:'):
            print("\n✅ El logo ya está en formato base64")
            print("No es necesario migrar")
            return
        
        # Verificar si es una ruta de archivo
        if config.logo_url and config.logo_url.startswith('/uploads/'):
            print("\n🔄 Migrando logo de archivo a base64...")
            
            # Extraer nombre del archivo
            filename = config.logo_url.split('/uploads/', 1)[1]
            
            # Buscar archivo en uploads/
            upload_dir = 'uploads'
            file_path = os.path.join(upload_dir, filename)
            
            if not os.path.exists(file_path):
                print(f"\n⚠️  Archivo no encontrado: {file_path}")
                print("El logo se establecerá como None (usará logo por defecto)")
                config.logo_url = None
                db.session.commit()
                print("✅ Configuración actualizada")
                return
            
            # Leer archivo
            try:
                with open(file_path, 'rb') as f:
                    logo_bytes = f.read()
                
                size_kb = len(logo_bytes) / 1024
                print(f"📁 Archivo encontrado: {filename} ({size_kb:.2f} KB)")
                
                # Determinar mimetype
                ext = os.path.splitext(filename)[1].lower()
                mimetype_map = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg'
                }
                mimetype = mimetype_map.get(ext, 'image/png')
                
                # Convertir a base64
                print(f"🔄 Convirtiendo a base64 ({mimetype})...")
                config.set_logo_from_file(logo_bytes, mimetype)
                
                # Guardar en BD
                db.session.commit()
                
                new_size_kb = config.get_logo_size_kb()
                print(f"✅ Logo migrado exitosamente")
                print(f"   Tamaño original: {size_kb:.2f} KB")
                print(f"   Tamaño base64: {new_size_kb:.2f} KB")
                print(f"   Incremento: {((new_size_kb / size_kb - 1) * 100):.1f}%")
                
                # Preguntar si eliminar archivo
                print(f"\n❓ ¿Deseas eliminar el archivo antiguo? ({file_path})")
                print("   El logo ya está guardado en la base de datos")
                respuesta = input("   Escribe 'si' para eliminar, cualquier otra cosa para mantener: ")
                
                if respuesta.lower() in ['si', 'sí', 's', 'yes', 'y']:
                    try:
                        os.remove(file_path)
                        print(f"🗑️  Archivo eliminado: {file_path}")
                        
                        # Verificar si la carpeta uploads está vacía
                        if os.path.exists(upload_dir) and not os.listdir(upload_dir):
                            print(f"📁 La carpeta {upload_dir}/ está vacía")
                            respuesta2 = input("   ¿Deseas eliminarla también? (si/no): ")
                            if respuesta2.lower() in ['si', 'sí', 's', 'yes', 'y']:
                                os.rmdir(upload_dir)
                                print(f"🗑️  Carpeta eliminada: {upload_dir}/")
                    except Exception as e:
                        print(f"⚠️  No se pudo eliminar el archivo: {e}")
                else:
                    print("📁 Archivo mantenido")
                
            except Exception as e:
                print(f"\n❌ Error al migrar: {e}")
                import traceback
                traceback.print_exc()
                return
        
        elif not config.logo_url:
            print("\n✅ No hay logo configurado")
            print("No es necesario migrar")
        
        else:
            print(f"\n⚠️  Formato de logo desconocido: {config.logo_url}")
            print("No se puede migrar automáticamente")
        
        print("\n" + "=" * 60)
        print("MIGRACIÓN COMPLETADA")
        print("=" * 60)


def main():
    """Punto de entrada principal"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "MIGRACIÓN DE LOGO A BASE64" + " " * 22 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\nEste script convierte logos almacenados como archivos")
    print("a formato base64 en la base de datos.\n")
    print("Ventajas:")
    print("  ✓ No necesita carpeta uploads/")
    print("  ✓ Todo en la base de datos")
    print("  ✓ Más simple en ejecutable")
    print("  ✓ Backup más fácil\n")
    
    try:
        migrate_logo_to_base64()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migración cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
