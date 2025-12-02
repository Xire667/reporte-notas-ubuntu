"""
Script de prueba para verificar el ícono de la bandeja del sistema
"""

from system_tray import create_system_tray
import time

def test_tray_icon():
    """Prueba el ícono de la bandeja del sistema"""
    print("=== Prueba del Ícono en la Bandeja del Sistema ===")
    print("1. Se abrirá el ícono en la bandeja del sistema")
    print("2. Busca el ícono en la bandeja (abajo a la derecha)")
    print("3. Haz clic derecho para ver el menú")
    print("4. Selecciona 'Salir' para cerrar")
    print("=" * 50)
    print("\nIniciando ícono de bandeja...")
    
    def on_quit():
        print("\n✓ Función de cierre ejecutada correctamente")
    
    tray = create_system_tray(on_quit_callback=on_quit)
    
    print("✓ Ícono creado")
    print("✓ Buscando archivo de ícono...")
    
    # Intentar cargar la imagen para verificar
    try:
        image = tray.create_image()
        print(f"✓ Ícono cargado: {image.size[0]}x{image.size[1]} píxeles")
        print(f"✓ Modo de color: {image.mode}")
    except Exception as e:
        print(f"✗ Error al cargar ícono: {e}")
    
    print("\n▶ Iniciando ícono en la bandeja del sistema...")
    print("  (Haz clic derecho en el ícono y selecciona 'Salir' para cerrar)")
    
    # Ejecutar el ícono (bloquea hasta que se cierre)
    tray.run()
    
    print("\n✓ Prueba completada")

if __name__ == '__main__':
    test_tray_icon()
