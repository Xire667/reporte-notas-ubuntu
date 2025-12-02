"""
Visor de logs para administradores
Permite ver, filtrar y descargar logs del sistema
"""

import os
import sys
from datetime import datetime, timedelta
from flask import current_app


class LogViewer:
    """Clase para gestionar la visualización de logs"""
    
    @staticmethod
    def get_log_directory():
        """Obtiene el directorio de logs"""
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.getcwd()
        return os.path.join(base_dir, 'logs')
    
    @staticmethod
    def get_log_files():
        """Obtiene lista de archivos de log disponibles"""
        log_dir = LogViewer.get_log_directory()
        
        if not os.path.exists(log_dir):
            return []
        
        files = []
        for filename in os.listdir(log_dir):
            if filename.endswith('.log'):
                filepath = os.path.join(log_dir, filename)
                stat = os.stat(filepath)
                files.append({
                    'name': filename,
                    'path': filepath,
                    'size': stat.st_size,
                    'size_mb': stat.st_size / (1024 * 1024),
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'created': datetime.fromtimestamp(stat.st_ctime)
                })
        
        # Ordenar por fecha de modificación (más reciente primero)
        files.sort(key=lambda x: x['modified'], reverse=True)
        return files
    
    @staticmethod
    def read_log_file(filename, lines=500, level_filter=None, search_term=None):
        """
        Lee un archivo de log con filtros opcionales
        
        Args:
            filename: Nombre del archivo de log
            lines: Número máximo de líneas a leer (desde el final)
            level_filter: Filtrar por nivel (INFO, WARNING, ERROR, etc.)
            search_term: Término de búsqueda
            
        Returns:
            dict con información del log
        """
        log_dir = LogViewer.get_log_directory()
        filepath = os.path.join(log_dir, filename)
        
        if not os.path.exists(filepath):
            return {
                'success': False,
                'error': 'Archivo no encontrado'
            }
        
        try:
            # Leer archivo
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
            
            # Tomar últimas N líneas
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            # Aplicar filtros
            filtered_lines = []
            for line in recent_lines:
                # Filtro por nivel
                if level_filter and level_filter.upper() not in line:
                    continue
                
                # Filtro por término de búsqueda
                if search_term and search_term.lower() not in line.lower():
                    continue
                
                filtered_lines.append(line)
            
            # Parsear líneas para extraer información
            parsed_entries = []
            for line in filtered_lines:
                entry = LogViewer._parse_log_line(line)
                if entry:
                    parsed_entries.append(entry)
            
            # Estadísticas
            stats = LogViewer._calculate_stats(all_lines)
            
            return {
                'success': True,
                'filename': filename,
                'total_lines': len(all_lines),
                'filtered_lines': len(filtered_lines),
                'entries': parsed_entries,
                'stats': stats
            }
            
        except Exception as e:
            current_app.logger.error(f'Error leyendo log {filename}: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def _parse_log_line(line):
        """Parsea una línea de log y extrae información"""
        try:
            # Formato: 2024-11-25 10:30:45,123 [INFO] module: mensaje
            parts = line.split(' ', 3)
            if len(parts) >= 4:
                date_str = parts[0]
                time_str = parts[1]
                level_str = parts[2].strip('[]')
                message = parts[3].strip()
                
                # Determinar color según nivel
                level_colors = {
                    'DEBUG': 'secondary',
                    'INFO': 'info',
                    'WARNING': 'warning',
                    'ERROR': 'danger',
                    'CRITICAL': 'danger'
                }
                
                return {
                    'timestamp': f"{date_str} {time_str}",
                    'level': level_str,
                    'message': message,
                    'color': level_colors.get(level_str, 'secondary'),
                    'raw': line.strip()
                }
        except Exception:
            pass
        
        # Si no se puede parsear, retornar línea cruda
        return {
            'timestamp': '',
            'level': 'UNKNOWN',
            'message': line.strip(),
            'color': 'secondary',
            'raw': line.strip()
        }
    
    @staticmethod
    def _calculate_stats(lines):
        """Calcula estadísticas de los logs"""
        stats = {
            'total': len(lines),
            'debug': 0,
            'info': 0,
            'warning': 0,
            'error': 0,
            'critical': 0
        }
        
        for line in lines:
            line_upper = line.upper()
            if '[DEBUG]' in line_upper:
                stats['debug'] += 1
            elif '[INFO]' in line_upper:
                stats['info'] += 1
            elif '[WARNING]' in line_upper:
                stats['warning'] += 1
            elif '[ERROR]' in line_upper:
                stats['error'] += 1
            elif '[CRITICAL]' in line_upper:
                stats['critical'] += 1
        
        return stats
    
    @staticmethod
    def clear_old_logs(days=30):
        """
        Elimina logs más antiguos que X días
        
        Args:
            days: Días de antigüedad
            
        Returns:
            dict con resultado
        """
        log_dir = LogViewer.get_log_directory()
        
        if not os.path.exists(log_dir):
            return {
                'success': False,
                'error': 'Directorio de logs no existe'
            }
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_files = []
        errors = []
        
        try:
            for filename in os.listdir(log_dir):
                if not filename.endswith('.log'):
                    continue
                
                # No eliminar el log actual
                if filename == 'app.log':
                    continue
                
                filepath = os.path.join(log_dir, filename)
                modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if modified_time < cutoff_date:
                    try:
                        os.remove(filepath)
                        deleted_files.append(filename)
                    except Exception as e:
                        errors.append(f"{filename}: {str(e)}")
            
            return {
                'success': True,
                'deleted': len(deleted_files),
                'files': deleted_files,
                'errors': errors
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_recent_errors(hours=24, limit=50):
        """
        Obtiene errores recientes
        
        Args:
            hours: Horas hacia atrás
            limit: Número máximo de errores
            
        Returns:
            Lista de errores
        """
        log_files = LogViewer.get_log_files()
        
        if not log_files:
            return []
        
        # Leer el log más reciente
        main_log = log_files[0]['name']
        result = LogViewer.read_log_file(main_log, lines=1000, level_filter='ERROR')
        
        if not result['success']:
            return []
        
        # Filtrar por tiempo
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = []
        
        for entry in result['entries']:
            try:
                # Parsear timestamp
                timestamp_str = entry['timestamp']
                # Formato: 2024-11-25 10:30:45,123
                timestamp = datetime.strptime(timestamp_str.split(',')[0], '%Y-%m-%d %H:%M:%S')
                
                if timestamp >= cutoff_time:
                    recent_errors.append(entry)
                    
                    if len(recent_errors) >= limit:
                        break
            except Exception:
                continue
        
        return recent_errors
