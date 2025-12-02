"""
Pantalla de carga (Splash Screen) para el Sistema de Gestión de Notas
Muestra el progreso de inicialización y maneja errores de forma visual
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os
import webbrowser
import logging
from io import StringIO


class SplashScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Gestión de Notas")
        
        # Configuración de la ventana
        window_width = 600
        window_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)  # Sin bordes de ventana
        
        # Variables de estado
        self.error_occurred = False
        self.error_message = ""
        self.app_instance = None
        
        # Crear interfaz
        self._create_widgets()
        
    def _create_widgets(self):
        """Crea los widgets de la interfaz"""
        # Frame principal con borde
        main_frame = tk.Frame(self.root, bg='white', relief='raised', borderwidth=2)
        main_frame.pack(fill='both', expand=True)
        
        # Logo/Título
        title_frame = tk.Frame(main_frame, bg='#00378F', height=80)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="Sistema de Gestión de Notas",
            font=('Arial', 18, 'bold'),
            bg='#00378F',
            fg='white'
        )
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(
            title_frame,
            text="Instituto Superior Tecnológico Público Suiza",
            font=('Arial', 10),
            bg='#00378F',
            fg='white'
        )
        subtitle_label.pack()
        
        # Área de contenido
        content_frame = tk.Frame(main_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Mensaje de estado
        self.status_label = tk.Label(
            content_frame,
            text="Iniciando sistema...",
            font=('Arial', 11),
            bg='white',
            fg='#333333'
        )
        self.status_label.pack(pady=(10, 5))
        
        # Barra de progreso
        self.progress = ttk.Progressbar(
            content_frame,
            mode='indeterminate',
            length=400
        )
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        # Área de log (oculta inicialmente)
        self.log_frame = tk.Frame(content_frame, bg='white')
        
        log_label = tk.Label(
            self.log_frame,
            text="Detalles de inicialización:",
            font=('Arial', 9, 'bold'),
            bg='white',
            fg='#666666'
        )
        log_label.pack(anchor='w', pady=(10, 5))
        
        # Text widget con scrollbar para logs
        log_container = tk.Frame(self.log_frame, bg='white')
        log_container.pack(fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(log_container)
        scrollbar.pack(side='right', fill='y')
        
        self.log_text = tk.Text(
            log_container,
            height=8,
            width=60,
            font=('Consolas', 8),
            bg='#f5f5f5',
            fg='#333333',
            yscrollcommand=scrollbar.set,
            wrap='word',
            state='disabled'
        )
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # Botones (ocultos inicialmente)
        self.button_frame = tk.Frame(content_frame, bg='white')
        
        self.retry_button = tk.Button(
            self.button_frame,
            text="Reintentar",
            command=self._retry,
            font=('Arial', 10),
            bg='#0d6efd',
            fg='white',
            padx=20,
            pady=5,
            relief='flat',
            cursor='hand2'
        )
        self.retry_button.pack(side='left', padx=5)
        
        self.close_button = tk.Button(
            self.button_frame,
            text="Cerrar",
            command=self._close,
            font=('Arial', 10),
            bg='#dc3545',
            fg='white',
            padx=20,
            pady=5,
            relief='flat',
            cursor='hand2'
        )
        self.close_button.pack(side='left', padx=5)
        
        # Footer
        footer_label = tk.Label(
            main_frame,
            text="Versión 1.0 | © 2024",
            font=('Arial', 8),
            bg='#f8f9fa',
            fg='#6c757d',
            pady=5
        )
        footer_label.pack(side='bottom', fill='x')
        
    def update_status(self, message):
        """Actualiza el mensaje de estado"""
        self.status_label.config(text=message)
        self.root.update()
        
    def add_log(self, message, level='info'):
        """Agrega un mensaje al log"""
        # Mostrar el frame de log si no está visible
        if not self.log_frame.winfo_ismapped():
            self.log_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        self.log_text.config(state='normal')
        
        # Colores según nivel
        colors = {
            'info': '#0d6efd',
            'success': '#198754',
            'warning': '#ffc107',
            'error': '#dc3545'
        }
        
        # Símbolos según nivel
        symbols = {
            'info': '●',
            'success': '✓',
            'warning': '⚠',
            'error': '✗'
        }
        
        color = colors.get(level, '#333333')
        symbol = symbols.get(level, '●')
        
        # Insertar mensaje con color
        self.log_text.insert('end', f"{symbol} ", f'symbol_{level}')
        self.log_text.insert('end', f"{message}\n")
        
        # Configurar tags de color
        self.log_text.tag_config(f'symbol_{level}', foreground=color, font=('Arial', 10, 'bold'))
        
        self.log_text.see('end')
        self.log_text.config(state='disabled')
        self.root.update()
        
    def show_error(self, title, message, details=None):
        """Muestra un error y detiene la carga"""
        self.error_occurred = True
        self.error_message = message
        
        self.progress.stop()
        self.progress.pack_forget()
        
        self.status_label.config(
            text=f"❌ Error: {title}",
            fg='#dc3545',
            font=('Arial', 11, 'bold')
        )
        
        if details:
            self.add_log(details, 'error')
        
        # Mostrar botones
        self.button_frame.pack(pady=20)
        
        self.root.update()
        
    def show_success(self):
        """Muestra mensaje de éxito y cierra la ventana"""
        self.progress.stop()
        self.progress.config(mode='determinate', value=100)
        
        self.status_label.config(
            text="✓ Sistema iniciado correctamente",
            fg='#198754',
            font=('Arial', 11, 'bold')
        )
        
        self.add_log("Abriendo navegador...", 'success')
        self.root.update()
        
        # Esperar un momento antes de cerrar
        self.root.after(1500, self._close_success)
        
    def _close_success(self):
        """Cierra la ventana después de éxito"""
        self.root.destroy()
        
    def _retry(self):
        """Reinicia el intento de inicialización"""
        # Resetear estado de error
        self.error_occurred = False
        self.error_message = ""
        
        # Ocultar botones
        self.button_frame.pack_forget()
        
        # Limpiar log
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.config(state='disabled')
        
        # Ocultar frame de log
        self.log_frame.pack_forget()
        
        # Resetear barra de progreso
        self.progress.config(mode='indeterminate', value=0)
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        # Resetear mensaje de estado
        self.status_label.config(
            text="Reintentando inicialización...",
            fg='#333333',
            font=('Arial', 11)
        )
        
        # Volver a ejecutar la inicialización
        if hasattr(self, '_init_func'):
            self.run_initialization(self._init_func)
        
    def _close(self):
        """Cierra la aplicación"""
        self.root.destroy()
        sys.exit(1)
        
    def run_initialization(self, init_func):
        """Ejecuta la función de inicialización en un thread separado"""
        # Guardar la función para poder reintentar
        self._init_func = init_func
        
        def worker():
            try:
                # Capturar logs
                log_capture = StringIO()
                handler = logging.StreamHandler(log_capture)
                handler.setLevel(logging.INFO)
                formatter = logging.Formatter('%(message)s')
                handler.setFormatter(formatter)
                
                # Ejecutar inicialización
                result = init_func(self)
                
                if result['success']:
                    self.root.after(0, self.show_success)
                    self.app_instance = result.get('app')
                else:
                    error_msg = result.get('error', 'Error desconocido')
                    details = result.get('details', '')
                    self.root.after(0, lambda: self.show_error(
                        "Error de inicialización",
                        error_msg,
                        details
                    ))
                    
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                self.root.after(0, lambda: self.show_error(
                    "Error inesperado",
                    str(e),
                    error_details
                ))
        
        # Iniciar thread
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        
    def run(self):
        """Inicia el loop de la ventana"""
        self.root.mainloop()
        return not self.error_occurred, self.app_instance


def create_splash_screen():
    """Crea y retorna una instancia de SplashScreen"""
    return SplashScreen()
