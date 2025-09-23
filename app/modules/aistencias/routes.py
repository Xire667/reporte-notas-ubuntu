

from flask import Flask,render_template

from . import asistencias_bp

@asistencias_bp.route('/')
def asistencias():
    return render_template('asistencias.html')