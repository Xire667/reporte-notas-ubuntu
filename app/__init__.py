from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Configuración
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    try:
        from config import config
        app.config.from_object(config[config_name])
    except ImportError:
        # Configuración por defecto si no existe config.py
        app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/sistema_academico'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # Configurar el cargador de usuarios
    from app.models import Usuario
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Registrar blueprints
    from .routes import blueprints
    for bp in blueprints:
        app.register_blueprint(bp)

    # Context processor para exponer ThemeConfig y logo en todas las plantillas
    from app.models import ThemeConfig

    @app.context_processor
    def inject_theme_config():
        try:
            # Si existieran múltiples filas, tomar la más reciente
            cfg = ThemeConfig.query.order_by(ThemeConfig.actualizado_en.desc()).first()
        except Exception as e:
            app.logger.error('Fallo al consultar ThemeConfig: %s', e)
            cfg = None
        s_logo = session.get('logo_url')
        # Log de diagnóstico: qué logo se usará en esta respuesta
        try:
            src = s_logo or (cfg.logo_url if cfg else None)
            app.logger.debug('Logo en uso (session/DB): %s', ('<none>' if not src else (src[:80] + ('…' if len(src) > 80 else ''))))
            if cfg and cfg.logo_url:
                app.logger.debug('ThemeConfig activo id=%s len(logo_url)=%s', cfg.id, len(cfg.logo_url))
        except Exception:
            pass
        return {
            'theme_config': cfg,
            'session_logo_url': s_logo
        }

    # Crear tablas en desarrollo si la conexión está disponible.
    # No abortar si la DB no existe todavía: run_server.py se encarga de crearla.
    try:
        with app.app_context():
            # Solo ejecutar create_all() en entorno de desarrollo.
            # En ejecutable (production), run_server.py se encarga de crear DB y tablas.
            if (config_name or os.environ.get('FLASK_ENV', 'development')) == 'development':
                db.create_all()
    except Exception as e:
        try:
            app.logger.warning('Omitiendo create_all() en create_app: %s', e)
        except Exception:
            pass
    
    return app