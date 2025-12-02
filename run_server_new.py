import webbrowser
import logging
import sys
import os
import traceback
from werkzeug.exceptions import HTTPException
from waitress import serve
from app import create_app, db
import mysql.connector
from mysql.connector import errorcode
from app.models import Usuario


def initialize_system(splash=None):
    """
    Inicializa el sistema y retorna el resultado
    
    Args:
        splash: Instancia de SplashScreen para actualizar el progreso
        
    Returns:
        dict: {'success': bool, 'app': Flask app, 'error': str, 'details': str}
    """
    def log(message, level='info'):
        """Helper para logging con splash"""
        if splash:
            splash.add_log(message, level)
        print(message)
    
    def update_status(message):
        """Helper para actualizar estado"""
        if splash:
            splash.update_status(message)
        print(f"[STATUS] {message}")
    
    try:
        update_status("Cargando configuración...")
        log("Iniciando Sistema de Gestión de Notas", 'info')
        
        # Usar configuración MySQL (XAMPP) definida en config.py / variables .env
        # Selección de configuración: en ejecutable (PyInstaller) forzar 'production'
        config_name = os.getenv('FLASK_ENV', 'development')
        if getattr(sys, 'frozen', False):
            config_name = 'production'
            log("Modo: Ejecutable (Production)", 'info')
        else:
            log("Modo: Desarrollo", 'info')
        
        update_status("Creando aplicación Flask...")
        app = create_app(config_name)
        log("Aplicación Flask creada", 'success')

        update_status("Configurando sistema de logs...")
        
        # Configurar logging detallado a consola
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        app.logger.setLevel(logging.DEBUG)
        logging.getLogger('waitress').setLevel(logging.INFO)
        logging.getLogger('werkzeug').setLevel(logging.INFO)

        # Logging a archivo con rotación
        try:
            base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd()
            logs_dir = os.path.join(base_dir, 'logs')
            os.makedirs(logs_dir, exist_ok=True)
            log_path = os.path.join(logs_dir, 'app.log')
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=5, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
            logging.getLogger().addHandler(file_handler)
            app.logger.info('File logging habilitado en %s', log_path)
            log(f"Logs guardados en: {log_path}", 'success')
        except Exception as e:
            app.logger.warning('No se pudo habilitar logging a archivo: %s', e)
            log(f"Advertencia: No se pudo crear archivo de log", 'warning')

        # Activar/Desactivar logging de SQL según DEBUG_SQL (por defecto desactivado)
        if os.getenv('DEBUG_SQL', '0') == '1':
            app.config['SQLALCHEMY_ECHO'] = True
            logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
            logging.getLogger('sqlalchemy.pool').setLevel(logging.INFO)
            app.logger.info('SQLAlchemy echo activado (DEBUG_SQL=1)')
        else:
            app.config['SQLALCHEMY_ECHO'] = False
            logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
            logging.getLogger('sqlalchemy.pool').setLevel(logging.ERROR)

        # Registrar manejador global de errores para ver trazas en consola
        def _log_exception(e):
            # No tratar HTTPException (404/400/etc.) como error interno
            if isinstance(e, HTTPException):
                app.logger.warning('HTTP %s %s', e.code, e.name)
                return e
            app.logger.exception('Excepción no controlada')
            return ('Error interno del servidor', 500)
        app.register_error_handler(Exception, _log_exception)

        update_status("Verificando conexión a MySQL...")
        
        # Verificación previa de credenciales y conectividad al servidor MySQL
        def preflight_mysql_connection():
            cfg = app.config
            db_host = cfg.get('DB_HOST')
            db_user = cfg.get('DB_USER')
            db_password = cfg.get('DB_PASSWORD')
            db_name = cfg.get('DB_NAME')

            if not db_name:
                error_msg = "Falta el nombre de la base de datos (DB_NAME)"
                log(error_msg, 'error')
                return False, error_msg, "Define DB_NAME en tu archivo .env"

            log(f"Conectando a MySQL: {db_user}@{db_host}", 'info')
            
            try:
                conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password)
                # Usar ping en lugar de SELECT para evitar resultados no leídos
                try:
                    conn.ping(reconnect=False, attempts=1, delay=0)
                except TypeError:
                    # Compatibilidad con versiones de mysql.connector sin argumentos en ping()
                    conn.ping()
                conn.close()
                app.logger.info('Conexión al servidor MySQL verificada (%s@%s)', db_user or '<vacío>', db_host)
                log(f"Conexión exitosa a MySQL", 'success')
                return True, None, None
            except mysql.connector.Error as me:
                # Errores comunes: servidor caído / credenciales inválidas
                if getattr(me, 'errno', None) == errorcode.ER_ACCESS_DENIED_ERROR:
                    error_msg = "Credenciales MySQL incorrectas"
                    details = f"Usuario: '{db_user or ''}' | Host: '{db_host or ''}'\n\nRevisa DB_USER y DB_PASSWORD en el archivo .env"
                    log(error_msg, 'error')
                    return False, error_msg, details
                elif getattr(me, 'errno', None) in (2003, 2005):
                    error_msg = "No se pudo conectar al servidor MySQL"
                    details = f"Asegúrate de que XAMPP esté encendido y MySQL activo (localhost:3306)\n\nError técnico: {me}"
                    log(error_msg, 'error')
                    return False, error_msg, details
                else:
                    error_msg = "Error al verificar conexión MySQL"
                    details = f"Detalle técnico: {me}"
                    log(error_msg, 'error')
                    return False, error_msg, details
            except Exception as e:
                error_msg = "Error inesperado al conectar a MySQL"
                details = f"Detalle técnico: {e}"
                log(error_msg, 'error')
                return False, error_msg, details

        # Ejecutar verificación previa; si falla, no continuar
        success, error_msg, error_details = preflight_mysql_connection()
        if not success:
            return {
                'success': False,
                'error': error_msg,
                'details': error_details
            }

        update_status("Verificando base de datos...")
        
        # Crear la base de datos si no existe, luego crear tablas y datos por defecto si está vacía
        def ensure_database_and_seed():
            cfg = app.config
            db_host = cfg.get('DB_HOST')
            db_user = cfg.get('DB_USER')
            db_password = cfg.get('DB_PASSWORD')
            db_name = cfg.get('DB_NAME')

            # Intentar conectar a MySQL sin especificar base para crearla si falta
            try:
                log(f"Verificando base de datos: {db_name}", 'info')
                conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password)
                cur = conn.cursor()
                cur.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
                cur.close()
                conn.close()
                app.logger.info('Verificada/creada base de datos: %s', db_name)
                log(f"Base de datos '{db_name}' lista", 'success')
            except mysql.connector.Error as me:
                app.logger.error('No se pudo conectar al servidor MySQL para crear DB: %s', me)
                error_msg = "Error al crear base de datos"
                details = f"Asegúrate de que XAMPP esté encendido y MySQL activo.\n\nDetalle técnico: {me}"
                log(error_msg, 'error')
                raise Exception(f"{error_msg}: {details}")

            # Con la DB ya creada/verificada, crear tablas y seed si está vacío
            update_status("Creando tablas de la base de datos...")
            with app.app_context():
                try:
                    db.create_all()
                    app.logger.info('Tablas verificadas/creadas correctamente')
                    log("Tablas de la base de datos creadas", 'success')
                except Exception as e:
                    app.logger.exception('Error al crear tablas: %s', e)
                    log(f"Error al crear tablas: {e}", 'error')
                    raise

                # Datos por defecto si no hay usuarios
                if not Usuario.query.first():
                    update_status("Creando usuarios por defecto...")
                    log("Creando usuarios por defecto (admin, docente, alumno)", 'info')
                    try:
                        admin = Usuario(
                            dni='12345678', nombre='Administrador', apellido='Sistema',
                            email='admin@sistema.edu', rol='admin'
                        )
                        admin.set_password('admin123')

                        docente = Usuario(
                            dni='87654321', nombre='Juan', apellido='Pérez',
                            email='juan.perez@sistema.edu', rol='docente'
                        )
                        docente.set_password('docente123')

                        alumno = Usuario(
                            dni='11223344', nombre='María', apellido='González',
                            email='maria.gonzalez@sistema.edu', rol='alumno'
                        )
                        alumno.set_password('alumno123')

                        db.session.add_all([admin, docente, alumno])
                        db.session.commit()
                        app.logger.info('Usuarios por defecto creados (admin/docente/alumno)')
                        log("Usuarios por defecto creados correctamente", 'success')
                    except Exception as e:
                        db.session.rollback()
                        app.logger.exception('Error creando usuarios por defecto: %s', e)
                        log(f"Advertencia: No se pudieron crear usuarios por defecto", 'warning')
                else:
                    log("Base de datos ya contiene usuarios", 'info')

        # Verificación de conectividad y autocreación de base si falta
        try:
            with app.app_context():
                conn = db.engine.connect()
                conn.close()
                log("Conexión a la base de datos verificada", 'success')
        except Exception as e:
            msg = str(e)
            # Si el error indica base desconocida, la creamos y continuamos
            if 'Unknown database' in msg or '1049' in msg:
                app.logger.warning('La base %s no existe. Intentando crear...', app.config.get('DB_NAME'))
                log(f"Base de datos no existe, creando...", 'warning')
                try:
                    ensure_database_and_seed()
                except Exception as create_error:
                    return {
                        'success': False,
                        'error': "Error al crear la base de datos",
                        'details': str(create_error)
                    }
            else:
                error_msg = "No se pudo conectar a la base de datos"
                details = f"Asegúrate de que XAMPP esté encendido y MySQL activo.\n\nDetalle técnico: {e}"
                log(error_msg, 'error')
                return {
                    'success': False,
                    'error': error_msg,
                    'details': details
                }

        update_status("Iniciando servidor web...")
        log("Preparando servidor Waitress en http://127.0.0.1:5000/", 'info')
        
        # Abrir navegador automáticamente en el puerto local
        url = 'http://127.0.0.1:5000/'
        try:
            webbrowser.open_new_tab(url)
            log("Navegador abierto automáticamente", 'success')
        except Exception:
            log("No se pudo abrir el navegador automáticamente", 'warning')

        # Retornar éxito con la app
        return {
            'success': True,
            'app': app
        }
        
    except Exception as e:
        error_msg = "Error inesperado durante la inicialización"
        details = traceback.format_exc()
        if splash:
            splash.add_log(error_msg, 'error')
        return {
            'success': False,
            'error': error_msg,
            'details': details
        }


def main():
    """Punto de entrada principal con splash screen"""
    # Verificar si estamos en modo GUI (ejecutable) o consola (desarrollo)
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        # Modo ejecutable: usar splash screen y system tray
        from splash_screen import create_splash_screen
        from system_tray import create_system_tray
        
        splash = create_splash_screen()
        splash.run_initialization(initialize_system)
        success, app_instance = splash.run()
        
        if success and app_instance:
            # Crear ícono en la bandeja del sistema
            tray_icon = create_system_tray(on_quit_callback=lambda: os._exit(0))
            tray_thread = tray_icon.start_in_thread()
            
            print('\n✓ Sistema iniciado correctamente')
            print('Servidor corriendo en http://127.0.0.1:5000/')
            print('Ícono en la bandeja del sistema para controlar el servidor')
            print('Haz clic derecho en el ícono para ver opciones')
            
            # Iniciar servidor (bloquea hasta que se cierre)
            try:
                serve(app_instance, host='127.0.0.1', port=5000)
            except KeyboardInterrupt:
                print('\n\nServidor detenido por el usuario')
            except Exception:
                print('\n❌ Error fatal al iniciar el servidor:')
                traceback.print_exc()
            finally:
                # Asegurar que el proceso termine
                os._exit(0)
    else:
        # Modo desarrollo: sin splash screen ni system tray
        result = initialize_system(splash=None)
        
        if result['success']:
            app = result['app']
            print('\n✓ Sistema iniciado correctamente')
            print('Servidor corriendo en http://127.0.0.1:5000/')
            print('Presiona Ctrl+C para detener el servidor')
            try:
                serve(app, host='127.0.0.1', port=5000)
            except KeyboardInterrupt:
                print('\n\nServidor detenido por el usuario')
            except Exception:
                print('\n❌ Error fatal al iniciar el servidor:')
                traceback.print_exc()
        else:
            print(f"\n❌ Error: {result['error']}")
            if result.get('details'):
                print(f"\nDetalles:\n{result['details']}")
            input("\nPresiona Enter para cerrar...")


if __name__ == '__main__':
    main()
