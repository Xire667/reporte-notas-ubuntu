# Sistema de Gestión de Notas - Instituto Suiza

Sistema web desarrollado en Flask para la gestión académica del Instituto Superior Tecnológico Público Suiza. Permite la administración de usuarios, cursos, calificaciones y seguimiento estudiantil.

## 🚀 Características Principales

### Roles del Sistema

#### 👨‍💼 Administrador
- Dashboard con estadísticas generales del sistema
- Gestión completa de docentes (CRUD)
- Gestión completa de cursos (CRUD)
- Asignación de cursos a docentes
- Gestión completa de alumnos (CRUD)
- Matrícula de alumnos en cursos
- Gestión de ciclos académicos
- Visualización y supervisión de notas
- Exportación de reportes (PDF/Excel)
- **Personalización de estilos del sistema**
- **Gestión de logo institucional**
- **Visualización de logs del sistema**
- **Control del servidor (apagar desde la interfaz)**

#### 👨‍🏫 Docente
- Vista de cursos asignados
- Lista de alumnos por curso
- Gestión de notas por parciales (Actividades, Prácticas, Parciales)
- Cálculo automático de promedio final (10% + 30% + 60%)
- Publicación de notas (borrador/publicada)
- Exportación de reportes por curso (PDF)
- Exportación de reportes por alumno (PDF)
- Importación masiva de notas desde Excel
- Exportación de plantilla Excel
- Comentarios y observaciones por alumno

#### 👨‍🎓 Alumno
- Dashboard personalizado con estadísticas
- Visualización de todas sus notas por curso
- Consulta de calificaciones detalladas (actividades, prácticas, parciales)
- Visualización de promedio final
- Seguimiento del rendimiento académico
- Solo ve notas publicadas por el docente
- **Descarga de PDF con notas por curso individual**
- **Descarga de PDF con resumen de todos los cursos y promedios**

## 🛠️ Tecnologías Utilizadas

- **Backend**: Flask 2.3.3
- **Base de Datos**: MySQL con SQLAlchemy 2.0.30
- **Autenticación**: Flask-Login 0.6.3
- **Frontend**: Bootstrap 5.3, HTML5, CSS3, JavaScript
- **Servidor WSGI**: Waitress 2.1.2
- **Exportación PDF**: xhtml2pdf 0.2.17, reportlab 4.4.4
- **Exportación Excel**: openpyxl 3.1.5
- **Interfaz Gráfica**: tkinter (incluido con Python)
- **System Tray**: pystray 0.19.5
- **Procesamiento de Imágenes**: Pillow

## 📋 Requisitos del Sistema

- Python 3.11 (recomendado)
- MySQL 5.7+ o MariaDB 10.3+
- XAMPP (recomendado para desarrollo)
- Windows 10/11 (para ejecutable)

## 🔧 Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd reporte-notas-ubuntu
```

### 2. Crear entorno virtual
```bash
# Crear el entorno virtual con Python 3.11
python -m venv venv311

# Activar en Windows
venv311\Scripts\activate

# Activar en Linux/Mac
source venv311/bin/activate
```

### 3. Instalar dependencias
```bash
# Dependencias de la aplicación
pip install -r requirements.txt

# Dependencias de desarrollo (solo si vas a compilar)
pip install -r requirements-dev.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` basado en `.env.example`:

```ini
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=sistema_academico
FLASK_ENV=development
```

### 5. Configurar MySQL

1. Inicia XAMPP y activa MySQL
2. La aplicación creará automáticamente la base de datos si no existe
3. Se crearán usuarios por defecto en el primer inicio

### 6. Ejecutar la aplicación

#### Modo Desarrollo:
```bash
python run_server_new.py
```

#### Modo Ejecutable:
```bash
# Compilar
build_exe.bat

# Ejecutar
cd dist
SistemaNotas.exe
```

La aplicación estará disponible en: `http://127.0.0.1:5000/`

## 🎯 Usuarios por Defecto

En el primer inicio, se crean automáticamente:

| Rol | DNI | Contraseña |
|-----|-----|------------|
| Administrador | 12345678 | admin123 |
| Docente | 87654321 | docente123 |
| Alumno | 11223344 | alumno123 |

**⚠️ Importante**: Cambia estas contraseñas después del primer inicio.

## 📦 Compilación del Ejecutable

### Requisitos:
- Python 3.11
- Todas las dependencias instaladas
- XAMPP con MySQL activo

### Pasos:

1. **Instalar dependencias de desarrollo**:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Compilar**:
   ```bash
   build_exe.bat
   ```

3. **Resultado**:
   - Ejecutable: `dist/SistemaNotas.exe`
   - Incluye: Splash screen, System tray, Auto-inicialización de BD

### Características del Ejecutable:

- ✅ **Splash Screen**: Pantalla de carga con progreso
- ✅ **Botón Reintentar**: Si MySQL no está activo, puedes reintentar sin cerrar
- ✅ **System Tray Icon**: Ícono en la bandeja del sistema para controlar el servidor
- ✅ **Auto-inicialización**: Crea la BD y usuarios automáticamente
- ✅ **Logs**: Guarda logs en `logs/app.log`
- ✅ **Sin consola**: Interfaz limpia sin ventana de comandos

## 🎮 Control del Servidor

### Opción 1: Ícono en la Bandeja del Sistema (Recomendado)

Cuando ejecutas el `.exe`, aparece un ícono en la bandeja del sistema:

- **Clic derecho** → **"Abrir en Navegador"**: Abre la aplicación
- **Clic derecho** → **"Salir"**: Cierra el servidor completamente

### Opción 2: Botón en el Panel de Administración

Solo para administradores:

1. Inicia sesión como administrador
2. En el menú lateral, busca **"Apagar Servidor"** (botón rojo al final)
3. Confirma y el servidor se cerrará

### Opción 3: Administrador de Tareas

Como último recurso:
1. Abre el Administrador de Tareas (Ctrl + Shift + Esc)
2. Busca "SistemaNotas.exe"
3. Finalizar tarea

## 📁 Estructura del Proyecto

```
reporte-notas-ubuntu/
├── app/
│   ├── __init__.py              # Configuración de Flask
│   ├── models.py                # Modelos de BD
│   ├── routes.py                # Registro de blueprints
│   ├── modules/
│   │   ├── auth/                # Autenticación
│   │   ├── admin/               # Panel administrador
│   │   │   ├── routes.py        # Rutas del admin
│   │   │   └── log_viewer.py   # Visor de logs
│   │   ├── docente/             # Panel docente
│   │   ├── alumno/              # Panel alumno
│   │   │   └── routes.py        # Rutas y descarga de PDFs
│   │   ├── main/                # Página principal
│   │   └── uploads/             # Gestión de archivos
│   ├── templates/               # Plantillas HTML
│   │   ├── alumno/
│   │   │   ├── notas_curso_pdf.html      # PDF notas por curso
│   │   │   └── resumen_cursos_pdf.html   # PDF resumen general
│   │   └── ...
│   └── static/                  # CSS, JS, imágenes
├── tools/
│   └── generate_ico.py          # Generador de ícono
├── config.py                    # Configuración de BD
├── run_server_new.py            # Punto de entrada principal
├── splash_screen.py             # Pantalla de carga
├── system_tray.py               # Ícono de bandeja
├── init_db.py                   # Inicializador de BD (opcional)
├── requirements.txt             # Dependencias
├── requirements-dev.txt         # Dependencias de desarrollo
├── build_exe.bat                # Script de compilación
└── README.md                    # Este archivo
```

## 🗄️ Base de Datos

### Tablas Principales:

- **usuarios**: Información de usuarios (admin, docentes, alumnos)
- **cursos**: Catálogo de cursos
- **curso_docente**: Asignación de cursos a docentes
- **curso_alumno**: Matrícula de alumnos
- **notas**: Tabla principal de calificaciones
- **notas_actividades**: Notas de actividades (10%)
- **notas_practicas**: Notas de prácticas (30%)
- **notas_parciales**: Notas de parciales (60%)
- **ciclos_academicos**: Períodos académicos
- **theme_config**: Configuración de estilos y logo

### Fórmula de Cálculo:

```
Promedio Final = (Actividades × 0.10) + (Prácticas × 0.30) + (Parciales × 0.60)
```

## 🎯 Funcionalidades Detalladas

### Gestión de Notas

#### Para Docentes:
1. **Ingreso Manual**: Formulario para ingresar notas individuales
2. **Importación Excel**: Carga masiva desde plantilla
3. **Estados**: Borrador (solo docente) o Publicada (visible para alumnos)
4. **Exportación**: Reportes en PDF por curso o por alumno

#### Para Alumnos:
- Solo ven notas con estado "Publicada"
- Vista detallada por curso
- Promedios calculados automáticamente
- **Descarga de PDF individual por curso**:
  - Todas las actividades (8)
  - Todas las prácticas (4)
  - Todos los parciales (2)
  - Promedios por categoría
  - Promedio final con estado (Aprobado/Desaprobado)
- **Descarga de PDF con resumen general**:
  - Lista de todos los cursos matriculados
  - Promedio final de cada curso
  - Estadísticas generales (cursos aprobados, desaprobados)
  - Promedio general de todos los cursos

### Personalización del Sistema

#### Editar Estilos (Admin):
- Cambiar colores del tema (oscuro, claro, medio)
- Subir logo institucional (PNG/JPG/JPEG)
- Logo se guarda en base64 (no requiere carpeta uploads)
- Vista previa en tiempo real

#### Logs del Sistema (Admin):
- Visualización de logs en tiempo real
- Filtrado por nivel (INFO, WARNING, ERROR)
- Búsqueda por texto
- Descarga de logs completos

### Reportes en PDF

#### Para Docentes:
1. **Reporte por Curso**: Lista completa de alumnos con todas sus notas
2. **Reporte por Alumno**: Detalle individual de un alumno específico

#### Para Alumnos:
1. **Reporte por Curso Individual**:
   - Información del alumno y curso
   - Todas las actividades (8) con sus notas
   - Todas las prácticas (4) con sus notas
   - Todos los parciales (2) con sus notas
   - Promedios por categoría (10%, 30%, 60%)
   - Promedio final destacado
   - Estado: Aprobado (≥10.5) o Desaprobado (<10.5)
   - Fórmula de cálculo incluida

2. **Resumen General de Cursos**:
   - Información del alumno
   - Estadísticas generales:
     - Total de cursos matriculados
     - Cursos calificados
     - Cursos aprobados
     - Cursos desaprobados
   - Tabla con todos los cursos y sus promedios
   - Promedio general de todos los cursos
   - Diseño compacto y profesional

**Características de los PDFs:**
- ✅ Diseño profesional con colores institucionales
- ✅ Formato A4 optimizado para impresión
- ✅ Tamaño compacto (fuentes 8-9pt)
- ✅ Descarga automática al hacer clic
- ✅ Nombres de archivo descriptivos
- ✅ Fecha de generación incluida

## 🎨 Interfaz de Usuario

- **Diseño responsive**: Se adapta a móviles, tablets y escritorio
- **Bootstrap 5**: Componentes modernos y accesibles
- **Font Awesome**: Iconos profesionales
- **Sidebar colapsable**: Navegación intuitiva
- **Colores semánticos**: Estados visuales claros
- **Animaciones suaves**: Transiciones fluidas

## 🔧 Personalización Avanzada

### Cambiar Puerto del Servidor

Editar `run_server_new.py`:
```python
serve(app_instance, host='127.0.0.1', port=5000)  # Cambiar 5000 por otro puerto
```

### Modificar Estilos CSS

Archivos principales:
- `app/static/main/styles/sistema.css` - Estilos generales
- `app/static/main/styles/admin.css` - Estilos del admin
- `app/static/main/styles/colores_base.css` - Variables de color

### Agregar Nuevos Módulos

1. Crear carpeta en `app/modules/nuevo_modulo/`
2. Crear `__init__.py` con el blueprint
3. Crear `routes.py` con las rutas
4. Registrar en `app/routes.py`
5. Crear templates en `app/templates/nuevo_modulo/`

## 🐛 Solución de Problemas

### El ejecutable no inicia

**Problema**: MySQL no está activo

**Solución**:
1. Abre XAMPP
2. Inicia MySQL
3. Presiona "Reintentar" en el splash screen

---

**Problema**: Error de credenciales

**Solución**:
1. Verifica el archivo `.env`
2. Asegúrate de que `DB_USER` y `DB_PASSWORD` sean correctos
3. Presiona "Reintentar"

---

### El ícono no aparece en la bandeja

**Solución**:
1. Verifica que estés ejecutando el `.exe` (no el script Python)
2. Busca en "Mostrar iconos ocultos" de la bandeja
3. Reinstala: `pip install pystray==0.19.5`

---

### Error al importar Excel

**Problema**: Formato incorrecto

**Solución**:
1. Descarga la plantilla desde el sistema
2. No modifies las columnas de la plantilla
3. Asegúrate de que las notas estén en el rango 0-20

---

### El logo no se ve

**Solución**:
1. Verifica que el archivo sea PNG, JPG o JPEG
2. Tamaño máximo: 5 MB
3. Recomendado: 256x256 píxeles o mayor

## 📚 Documentación Adicional

- **Manual de Usuario**: `Manual.txt`
- **Guía de Compilación**: `README_COMPILACION.md`
- **Instrucciones de Cierre**: `INSTRUCCIONES_CIERRE_SERVIDOR.md`
- **Cambios del Ícono**: `RESUMEN_CAMBIOS_ICONO.md`

## 🧪 Scripts de Prueba

- `test_splash_retry.py`: Prueba el botón Reintentar del splash screen
- `test_system_tray.py`: Prueba el ícono de la bandeja del sistema
- `init_db.py`: Inicializa la BD manualmente (opcional)

## 📊 Estadísticas del Proyecto

- **Lenguaje**: Python 3.11
- **Framework**: Flask 2.3.3
- **Líneas de código**: ~12,000+
- **Módulos**: 6 (auth, admin, docente, alumno, main, uploads)
- **Plantillas HTML**: 35+
- **Rutas**: 85+
- **Modelos de BD**: 11
- **Reportes PDF**: 4 tipos (docente por curso, docente por alumno, alumno por curso, alumno resumen general)

## 🔐 Seguridad

- ✅ Autenticación con Flask-Login
- ✅ Contraseñas hasheadas con Werkzeug
- ✅ Validación de roles en cada ruta
- ✅ Protección CSRF en formularios
- ✅ Validación de datos de entrada
- ✅ Sesiones seguras con SECRET_KEY
- ✅ Solo administradores pueden apagar el servidor

## 🚀 Próximas Mejoras

- [ ] Notificaciones por correo electrónico
- [ ] Recuperación de contraseña
- [ ] Historial de cambios en notas
- [ ] Gráficos de rendimiento (charts.js)
- [ ] Exportación a otros formatos (CSV, JSON)
- [ ] API REST para integración con otros sistemas
- [ ] Modo oscuro/claro automático
- [ ] Firma digital en PDFs
- [ ] Comparación de rendimiento entre ciclos

## 📞 Soporte

Para soporte técnico o reportar problemas:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo
- Revisar los logs en `logs/app.log`

## 📄 Licencia

Este proyecto está desarrollado para el Instituto Superior Tecnológico Público Suiza.

---

**Desarrollado con ❤️ para la educación tecnológica**

**Versión**: 2.1  
**Última actualización**: Diciembre 2024

## 🆕 Novedades de la Versión 2.1

### Nuevas Funcionalidades para Alumnos:
- ✅ **Descarga de PDF por curso**: Los alumnos pueden descargar un reporte detallado de sus notas en cada curso
- ✅ **Descarga de PDF resumen general**: Los alumnos pueden descargar un resumen con todos sus cursos y promedios
- ✅ **Diseño optimizado**: PDFs compactos y profesionales, listos para imprimir

### Mejoras Generales:
- ✅ **Botón Reintentar funcional**: En el splash screen, si MySQL no está activo
- ✅ **Ícono en bandeja del sistema**: Control del servidor desde la bandeja de Windows
- ✅ **Botón Apagar Servidor**: Los administradores pueden apagar el servidor desde la interfaz
- ✅ **Mejor manejo de errores**: Validaciones mejoradas en todas las rutas
