

from flask import Flask,render_template

from . import main_bp

@main_bp.route('/')

def index():
    return render_template('main/inicio.html')