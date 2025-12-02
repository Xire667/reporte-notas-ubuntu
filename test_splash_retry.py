"""
Script de prueba para verificar el funcionamiento del botón Reintentar
en el splash screen
"""

from splash_screen import create_splash_screen
import time

# Contador de intentos para simular
attempt_count = 0

def test_initialization(splash):
    """
    Función de prueba que simula la inicialización
    Falla en el primer intento y tiene éxito en el segundo
    """
    global attempt_count
    attempt_count += 1
    
    splash.update_status(f"Intento #{attempt_count}...")
    splash.add_log(f"Iniciando intento de conexión #{attempt_count}", 'info')
    
    # Simular trabajo
    time.sleep(1)
    splash.add_log("Verificando conexión a MySQL...", 'info')
    time.sleep(1)
    
    # Fallar en el primer intento, éxito en el segundo
    if attempt_count == 1:
        splash.add_log("No se pudo conectar al servidor MySQL", 'error')
        return {
            'success': False,
            'error': "No se pudo conectar al servidor MySQL",
            'details': "Asegúrate de que XAMPP esté encendido y MySQL activo.\n\nEste es un error simulado para probar el botón Reintentar."
        }
    else:
        splash.add_log("Conexión exitosa a MySQL", 'success')
        time.sleep(0.5)
        splash.add_log("Base de datos verificada", 'success')
        time.sleep(0.5)
        splash.add_log("Sistema listo", 'success')
        return {
            'success': True,
            'app': None  # En la app real, aquí iría la instancia de Flask
        }


if __name__ == '__main__':
    print("=== Prueba del Splash Screen con Reintentar ===")
    print("1. El primer intento fallará (simulado)")
    print("2. Presiona 'Reintentar' para intentar de nuevo")
    print("3. El segundo intento será exitoso")
    print("=" * 50)
    
    splash = create_splash_screen()
    splash.run_initialization(test_initialization)
    success, app = splash.run()
    
    if success:
        print("\n✓ Prueba exitosa: El botón Reintentar funciona correctamente")
    else:
        print("\n✗ Prueba cancelada por el usuario")
