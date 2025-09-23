from flask import Blueprint

docente_bp = Blueprint('docente', __name__, url_prefix='/docente')

from . import routes
