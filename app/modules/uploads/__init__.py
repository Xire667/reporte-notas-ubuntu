from flask import Blueprint, send_from_directory
import os
import sys

uploads_bp = Blueprint('uploads', __name__)


def get_persistent_upload_dir() -> str:
    """Devuelve la carpeta de uploads persistente junto al ejecutable o CWD.

    - En modo empaquetado (PyInstaller one-file), usa el directorio del ejecutable.
    - En modo desarrollo, usa el directorio actual.
    """
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(os.getcwd())
    upload_dir = os.path.join(base_dir, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


@uploads_bp.route('/uploads/<path:filename>')
def serve_upload(filename: str):
    """Sirve archivos desde la carpeta de uploads persistente."""
    return send_from_directory(get_persistent_upload_dir(), filename)