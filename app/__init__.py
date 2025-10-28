from flask import Flask, url_for
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

    # Context processor: expone URL del logo para la barra de navegación
    @app.context_processor
    def inject_navbar_logo():
        try:
            uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
            logo_file = os.path.join(uploads_dir, 'logo.png')
            if os.path.exists(logo_file):
                return {'navbar_logo_url': url_for('static', filename='uploads/logo.png')}
        except Exception:
            pass
        return {'navbar_logo_url': None}

    # Crear tablas de la base de datos
    with app.app_context():
        db.create_all()
    
    return app