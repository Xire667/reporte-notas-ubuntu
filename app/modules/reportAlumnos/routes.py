from flask import Flask, render_template
from app.modules.reportAlumnos import report_bp

@report_bp.route('/report')
def reporte():
    
    return render_template('reporteAlumnos/index.html')
