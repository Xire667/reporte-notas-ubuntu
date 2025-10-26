"""
Sistema de Notas - Aplicación Principal
======================================
Este archivo es el punto de entrada principal de la aplicación.
Inicializa y ejecuta el servidor Flask para el sistema de gestión de notas académicas.
"""

# Importamos la función create_app desde el paquete app
from app import create_app

# Creamos la instancia de la aplicación Flask
app = create_app()

# Bloque principal: ejecuta el servidor solo si este archivo se ejecuta directamente
if __name__ == '__main__':
    # Inicia el servidor en modo debug (desarrollo)
    # En producción, se recomienda cambiar debug=False
    app.run(debug=True)