from flask import Blueprint

alumno_bp = Blueprint('alumno', __name__, url_prefix='/alumno')

from . import routes
