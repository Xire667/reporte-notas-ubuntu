"""
Ícono en la bandeja del sistema para controlar el servidor
"""

import pystray
from PIL import Image
import threading
import sys
import os


class SystemTrayIcon:
    def __init__(self, on_quit_callback=None):
        self.on_quit_callback = on_quit_callback
        self.icon = None
        
    def create_image(self):
        """Carga el ícono del ejecutable o crea uno simple si no existe"""
        # Intentar cargar el ícono del ejecutable
        icon_paths = [
            # Ruta cuando está empaquetado con PyInstaller
            os.path.join(sys._MEIPASS, 'app', 'static', 'main', 'assets', 'img', 'logo-dsi.ico') if getattr(sys, 'frozen', False) else None,
            # Ruta en desarrollo
            os.path.join('app', 'static', 'main', 'assets', 'img', 'logo-dsi.ico'),
            # Ruta alternativa
            os.path.join(os.path.dirname(__file__), 'app', 'static', 'main', 'assets', 'img', 'logo-dsi.ico'),
        ]
        
        # Intentar cargar el ícono desde las rutas posibles
        for icon_path in icon_paths:
            if icon_path and os.path.exists(icon_path):
                try:
                    # Cargar el ícono .ico
                    image = Image.open(icon_path)
                    # Convertir a RGB si es necesario
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    return image
                except Exception as e:
                    print(f"No se pudo cargar el ícono desde {icon_path}: {e}")
                    continue
        
        # Si no se pudo cargar, crear un ícono simple como fallback
        print("Usando ícono simple como fallback")
        from PIL import ImageDraw
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), 'white')
        dc = ImageDraw.Draw(image)
        
        # Dibujar círculo azul
        dc.ellipse([8, 8, 56, 56], fill='#00378F', outline='#00378F')
        
        # Dibujar "N" en blanco (simplificado)
        dc.rectangle([20, 20, 24, 44], fill='white')
        dc.rectangle([40, 20, 44, 44], fill='white')
        dc.polygon([24, 20, 40, 44, 40, 40, 28, 20], fill='white')
        
        return image
    
    def on_quit(self, icon, item):
        """Callback cuando se selecciona Salir"""
        print("Cerrando servidor...")
        icon.stop()
        
        if self.on_quit_callback:
            self.on_quit_callback()
        
        # Forzar salida
        os._exit(0)
    
    def on_open_browser(self, icon, item):
        """Abre el navegador con la aplicación"""
        import webbrowser
        webbrowser.open_new_tab('http://127.0.0.1:5000/')
    
    def run(self):
        """Inicia el ícono en la bandeja del sistema"""
        # Crear menú
        menu = pystray.Menu(
            pystray.MenuItem(
                "Abrir en Navegador",
                self.on_open_browser,
                default=True
            ),
            pystray.MenuItem(
                "Salir",
                self.on_quit
            )
        )
        
        # Crear ícono
        self.icon = pystray.Icon(
            "sistema_notas",
            self.create_image(),
            "Sistema de Gestión de Notas\nServidor activo en puerto 5000",
            menu
        )
        
        # Ejecutar (bloquea hasta que se cierre)
        self.icon.run()
    
    def start_in_thread(self):
        """Inicia el ícono en un thread separado"""
        thread = threading.Thread(target=self.run, daemon=False)
        thread.start()
        return thread


def create_system_tray(on_quit_callback=None):
    """Crea y retorna una instancia del ícono de bandeja"""
    return SystemTrayIcon(on_quit_callback)
