from app.modules.main import main_bp
from app.modules.auth import auth_bp
from app.modules.admin import admin_bp
from app.modules.docente import docente_bp
from app.modules.alumno import alumno_bp
from app.modules.uploads import uploads_bp

blueprints=[
    main_bp,
    auth_bp,
    admin_bp,
    docente_bp,
    alumno_bp,
    uploads_bp
]