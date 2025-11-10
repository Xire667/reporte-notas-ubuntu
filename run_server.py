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


def main():
    # Usar configuración MySQL (XAMPP) definida en config.py / variables .env
    # Selección de configuración: en ejecutable (PyInstaller) forzar 'production'
    config_name = os.getenv('FLASK_ENV', 'development')
    if getattr(sys, 'frozen', False):
        config_name = 'production'
    app = create_app(config_name)

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
    except Exception as e:
        app.logger.warning('No se pudo habilitar logging a archivo: %s', e)

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

    # Verificación previa de credenciales y conectividad al servidor MySQL
    def preflight_mysql_connection():
        cfg = app.config
        db_host = cfg.get('DB_HOST')
        db_user = cfg.get('DB_USER')
        db_password = cfg.get('DB_PASSWORD')
        db_name = cfg.get('DB_NAME')

        if not db_name:
            print("\n❌ Falta el nombre de la base de datos (DB_NAME).")
            print("Define DB_NAME en tu archivo .env o en config.py.")
            try:
                input("Presiona Enter para cerrar...")
            except Exception:
                pass
            return False

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
            return True
        except mysql.connector.Error as me:
            # Errores comunes: servidor caído / credenciales inválidas
            if getattr(me, 'errno', None) == errorcode.ER_ACCESS_DENIED_ERROR:
                print("\n❌ Credenciales MySQL incorrectas (ER_ACCESS_DENIED_ERROR 1045).")
                print("Revisa DB_USER y DB_PASSWORD en .env o config.py.")
                print(f"Intentado: usuario='{db_user or ''}' host='{db_host or ''}'")
            elif getattr(me, 'errno', None) in (2003, 2005):
                # 2003: Can't connect to MySQL server; 2005: Unknown MySQL server host
                print("\n❌ No se pudo conectar al servidor MySQL.")
                print("Asegúrate de que XAMPP esté encendido y MySQL activo (localhost:3306).")
                print(f"Detalle técnico (errno {me.errno}): {me}")
            else:
                print("\n❌ Error al verificar conexión MySQL.")
                print(f"Detalle técnico: {me}")
            try:
                input("Presiona Enter para cerrar...")
            except Exception:
                pass
            return False
        except Exception as e:
            print("\n❌ Error inesperado al verificar conexión MySQL.")
            print(f"Detalle técnico: {e}")
            try:
                input("Presiona Enter para cerrar...")
            except Exception:
                pass
            return False

    # Ejecutar verificación previa; si falla, no continuar
    if not preflight_mysql_connection():
        return

    # Crear la base de datos si no existe, luego crear tablas y datos por defecto si está vacía
    def ensure_database_and_seed():
        cfg = app.config
        db_host = cfg.get('DB_HOST')
        db_user = cfg.get('DB_USER')
        db_password = cfg.get('DB_PASSWORD')
        db_name = cfg.get('DB_NAME')

        # Intentar conectar a MySQL sin especificar base para crearla si falta
        try:
            conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password)
            cur = conn.cursor()
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cur.close()
            conn.close()
            app.logger.info('Verificada/creada base de datos: %s', db_name)
        except mysql.connector.Error as me:
            # Si el servidor no está disponible, salimos con mensaje.
            app.logger.error('No se pudo conectar al servidor MySQL para crear DB: %s', me)
            print("\n❌ No se pudo conectar al servidor MySQL.")
            print("Asegúrate de que XAMPP esté encendido y el servicio MySQL activo (localhost:3306).")
            print("Verifica credenciales en archivo .env o en config.py (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME).")
            print(f"Detalle técnico: {me}\n")
            try:
                input("Presiona Enter para cerrar...")
            except Exception:
                pass
            raise

        # Con la DB ya creada/verificada, crear tablas y seed si está vacío
        with app.app_context():
            try:
                db.create_all()
                app.logger.info('Tablas verificadas/creadas correctamente')
            except Exception as e:
                app.logger.exception('Error al crear tablas: %s', e)
                raise

            # Datos por defecto si no hay usuarios
            if not Usuario.query.first():
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
                except Exception as e:
                    db.session.rollback()
                    app.logger.exception('Error creando usuarios por defecto: %s', e)

    # Verificación de conectividad y autocreación de base si falta
    try:
        with app.app_context():
            conn = db.engine.connect()
            conn.close()
    except Exception as e:
        msg = str(e)
        # Si el error indica base desconocida, la creamos y continuamos
        if 'Unknown database' in msg or '1049' in msg:
            app.logger.warning('La base %s no existe. Intentando crear...', app.config.get('DB_NAME'))
            try:
                ensure_database_and_seed()
            except Exception:
                return
        else:
            print("\n❌ No se pudo conectar a MySQL.")
            print("Asegúrate de que XAMPP esté encendido y el servicio MySQL activo (localhost:3306).")
            print("Verifica credenciales en archivo .env o en config.py (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME).")
            print(f"Detalle técnico: {e}\n")
            try:
                input("Presiona Enter para cerrar...")
            except Exception:
                pass
            return

    # Abrir navegador automáticamente en el puerto local
    url = 'http://127.0.0.1:5000/'
    try:
        webbrowser.open_new_tab(url)
    except Exception:
        pass

    # Servidor WSGI de producción para Windows
    app.logger.info('Iniciando servidor en http://127.0.0.1:5000/')
    try:
        serve(app, host='127.0.0.1', port=5000)
    except Exception:
        print('\n❌ Error fatal al iniciar el servidor:')
        traceback.print_exc()
        try:
            input('Presiona Enter para cerrar...')
        except Exception:
            pass


if __name__ == '__main__':
    main()