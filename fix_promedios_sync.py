"""
Script para sincronizar promedios entre tablas relacionadas y tabla principal Nota
"""
from app import create_app, db
from app.models import Nota, NotaActividades, NotaPracticas, NotaParcial
from datetime import datetime

def sincronizar_promedios():
    """Sincroniza todos los promedios de las tablas relacionadas a la tabla principal"""
    app = create_app()
    
    with app.app_context():
        print("=== INICIANDO SINCRONIZACIÓN DE PROMEDIOS ===\n")
        
        # Obtener todas las notas
        notas = Nota.query.all()
        total = len(notas)
        actualizadas = 0
        sin_cambios = 0
        errores = 0
        
        for nota in notas:
            try:
                cambios = False
                promedio_anterior = nota.promedio_final
                
                # Sincronizar desde tablas relacionadas
                if nota.nota_actividades_id:
                    na = NotaActividades.query.get(nota.nota_actividades_id)
                    if na and na.promedio_actividades != nota.promedio_actividades:
                        nota.promedio_actividades = na.promedio_actividades
                        cambios = True
                        print(f"  Nota {nota.id}: Actividades {nota.promedio_actividades} -> {na.promedio_actividades}")
                
                if nota.nota_practicas_id:
                    np = NotaPracticas.query.get(nota.nota_practicas_id)
                    if np and np.promedio_practicas != nota.promedio_practicas:
                        nota.promedio_practicas = np.promedio_practicas
                        cambios = True
                        print(f"  Nota {nota.id}: Prácticas {nota.promedio_practicas} -> {np.promedio_practicas}")
                
                if nota.nota_parcial_id:
                    npa = NotaParcial.query.get(nota.nota_parcial_id)
                    if npa and npa.promedio_parciales != nota.promedio_parciales:
                        nota.promedio_parciales = npa.promedio_parciales
                        cambios = True
                        print(f"  Nota {nota.id}: Parciales {nota.promedio_parciales} -> {npa.promedio_parciales}")
                
                # Recalcular promedio final si hubo cambios
                if cambios:
                    nota.calcular_promedio_final()
                    nota.fecha_actualizacion = datetime.utcnow()
                    
                    print(f"✓ Nota {nota.id} (Alumno {nota.alumno_id}, Curso {nota.curso_id}):")
                    print(f"    Promedio Final: {promedio_anterior} -> {nota.promedio_final}")
                    print(f"    Estado: {nota.estado}\n")
                    
                    actualizadas += 1
                else:
                    sin_cambios += 1
                    
            except Exception as e:
                errores += 1
                print(f"✗ Error en Nota {nota.id}: {str(e)}\n")
        
        # Guardar cambios
        try:
            db.session.commit()
            print("\n=== RESUMEN ===")
            print(f"Total de notas: {total}")
            print(f"Actualizadas: {actualizadas}")
            print(f"Sin cambios: {sin_cambios}")
            print(f"Errores: {errores}")
            print("\n✓ Sincronización completada exitosamente")
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error al guardar cambios: {str(e)}")

if __name__ == '__main__':
    sincronizar_promedios()
