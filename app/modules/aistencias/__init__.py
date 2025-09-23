from flask import Blueprint
asistencias_bp=Blueprint('aistencias',__name__,
                         url_prefix='/asistencias',
                         template_folder='../../templates/asistencias')
from . import routes