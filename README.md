# Sistema de Gestión de Notas - Instituto Suiza

Sistema web desarrollado en Flask para la gestión académica del Instituto Superior Tecnológico Público Suiza. Permite la administración de usuarios, cursos, calificaciones y seguimiento estudiantil.

## 🚀 Características Principales

### Roles del Sistema

#### 👨‍💼 Administrador
- Registro y gestión de docentes
- Registro y gestión de cursos
- Asignación de cursos a docentes
- Registro y matrícula de alumnos
- Supervisión general del sistema

#### 👨‍🏫 Docente
- Subir y editar notas de alumnos
- Visualizar lista de alumnos por curso
- Gestión de calificaciones por parciales
- Comentarios y observaciones

#### 👨‍🎓 Alumno
- Inicio de sesión con DNI y contraseña
- Visualización de todas sus notas
- Consulta de calificaciones por curso
- Seguimiento del rendimiento académico

## 🛠️ Tecnologías Utilizadas

- **Backend**: Flask 3.1.1
- **Base de Datos**: MySQL con SQLAlchemy
- **Autenticación**: Flask-Login
- **Frontend**: Bootstrap 5.3, HTML5, CSS3, JavaScript
- **ORM**: SQLAlchemy 2.0.30
- **Templates**: Jinja2

## 📋 Requisitos del Sistema

- Python 3.11 (recomendado)
- MySQL 5.7+ o MariaDB 10.3+
- XAMPP (recomendado para desarrollo)

## 🔧 Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd reporte-notas-ubuntu
```

### 2. Crear entorno virtual (venv311)
```bash
# Crear el entorno virtual con Python 3.11
python -m venv venv311

# En Windows
venv311\Scripts\activate

# En Linux/Mac
source venv311/bin/activate
```

> Nota: el entorno virtual no se sube a GitHub. Cada colaborador crea su propio `venv311` local y ejecuta `pip install -r requirements.txt`. El archivo `.gitignore` ya excluye `venv/`, `venv311/` y `.venv/`.

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

Para construir el ejecutable en desarrollo, instala además las dependencias de build:
```bash
pip install -r requirements-dev.txt
```

### 4. Configurar la base de datos

#### Opción A: Usando XAMPP
1. Iniciar XAMPP
2. Activar Apache y MySQL
3. Abrir phpMyAdmin (http://localhost/phpmyadmin)
4. Crear una nueva base de datos llamada `sistema_academico`
5. Importar el archivo `README.md` (contiene el script SQL)

#### Opción B: MySQL directo
```sql
CREATE DATABASE sistema_academico;
USE sistema_academico;
-- Ejecutar el script SQL del README.md
```

### 5. Configurar la aplicación

Configura tu `.env` a partir de `.env.example` (no se sube a GitHub):

```ini
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=sistema_academico
FLASK_ENV=development
```

La aplicación lee variables desde `.env` usando `config.py`.

### 6. Ejecutar la aplicación (desarrollo)
```bash
python run_server.py
```

La aplicación estará disponible en: `http://127.0.0.1:5000/`

## 🚀 Distribución como ejecutable en Windows

Sigue estos pasos para crear un ejecutable que arranque el servidor local y abra el navegador automáticamente.

### 1) Preparar entorno
- Activa tu entorno virtual y luego instala dependencias:
  ```powershell
  venv\Scripts\activate
  pip install -r requirements.txt
  pip install pyinstaller
  ```
- Configura tu `.env` (puedes copiar desde `.env.example`):
  ```ini
  SECRET_KEY=tu_clave_secreta_muy_segura_aqui
  DB_HOST=localhost
  DB_USER=root
  DB_PASSWORD=
  DB_NAME=sistema_academico
  FLASK_ENV=development
  ```

### 2) Script de arranque
- Usa `run_server.py` (incluido) que:
  - Conecta a MySQL (XAMPP) usando `config.py` y tu `.env`.
  - Verifica conectividad a MySQL antes de iniciar.
  - Arranca el servidor WSGI con `waitress` en `http://127.0.0.1:5000/`.
  - Abre el navegador automáticamente.

### 3) Generar el ejecutable
- Opción A (recomendada): usa el script `build_exe.bat`:
  ```powershell
  .\build_exe.bat
  ```
- Opción B: comando PyInstaller manual (usa `;` en `--add-data` en Windows):
  ```powershell
  pyinstaller --noconfirm --clean ^
    --add-data "app/templates;app/templates" ^
    --add-data "app/static;app/static" ^
    --add-data ".env;." ^
    --name "SistemaNotas" run_server.py
  ```

### 4) Primera ejecución y base de datos
- Enciende XAMPP y activa `MySQL`.
- Ajusta `.env` con tus credenciales.
- El `.exe` verifica el servidor MySQL y credenciales; si la base `DB_NAME` no existe, la crea, crea tablas y hace seed inicial.

### 5) Opcional: Instalador MSI/EXE
- Usa Inno Setup o NSIS para crear un instalador que:
  - Copie `dist/SistemaNotas/`.
  - Cree accesos directos.
  - Incluya `.env` y archivos necesarios.

### 6) Notas
- `waitress` es adecuado para Windows y entorno local.
- Comprueba firewall/antivirus si hay bloqueos.

## 📁 Estructura del Proyecto

```
reporte-notas-ubuntu/
├── app/
│   ├── __init__.py              # Configuración principal de Flask
│   ├── models.py                # Modelos de la base de datos
│   ├── routes.py                # Registro de blueprints
│   ├── modules/
│   │   ├── auth/                # Autenticación y login
│   │   ├── admin/               # Gestión administrativa
│   │   ├── docente/             # Funcionalidades del docente
│   │   ├── alumno/              # Funcionalidades del alumno
│   │   └── main/                # Página principal
│   ├── templates/               # Plantillas HTML
│   │   ├── global/              # Plantillas base
│   │   ├── auth/                # Login y registro
│   │   ├── admin/               # Panel administrador
│   │   ├── docente/             # Panel docente
│   │   └── alumno/              # Panel alumno
│   └── static/                  # Archivos estáticos
│       └── main/
│           └── styles/          # CSS personalizado
├── run_server.py                # Punto de entrada recomendado
├── requirements.txt             # Dependencias de Python
├── build_exe.bat                # Script para empaquetar con PyInstaller
└── README.md                    # Este archivo

## 🧰 Buenas prácticas para subir a GitHub

- No subas: `venv/`, `venv311/`, `.venv/`, `dist/`, `build/`, `logs/`, `.env`.
- Asegúrate de que `requirements.txt` esté actualizado (`pip freeze > requirements.txt`).
- Usa `.env.example` para compartir la forma de configurar variables sin exponer credenciales.
- Documenta versiones recomendadas (Python 3.11) y comandos de setup (crear venv, instalar dependencias).
```

## 🗄️ Estructura de la Base de Datos

### Tablas Principales

- **usuarios**: Información de usuarios (admin, docentes, alumnos)
- **cursos**: Catálogo de cursos disponibles
- **curso_docente**: Asignación de cursos a docentes
- **curso_alumno**: Matrícula de alumnos en cursos
- **notas**: Calificaciones de los alumnos

### Script de Creación

El archivo `README.md` contiene el script SQL completo para crear todas las tablas necesarias.

## 🔐 Configuración de Usuarios

### Crear Usuario Administrador

1. Acceder a la aplicación
2. Ir a "Registrarse"
3. Seleccionar rol "Administrador"
4. Completar los datos requeridos

### Primer Uso

1. **Administrador**: Crear docentes y cursos
2. **Asignar cursos**: Vincular docentes con sus cursos
3. **Registrar alumnos**: Crear cuentas de estudiantes
4. **Matricular**: Asignar alumnos a cursos específicos

## 🎯 Funcionalidades por Rol

### Administrador
- ✅ Dashboard con estadísticas generales
- ✅ CRUD completo de docentes
- ✅ CRUD completo de cursos
- ✅ CRUD completo de alumnos
- ✅ Asignación de cursos a docentes
- ✅ Matrícula de alumnos en cursos

### Docente
- ✅ Vista de cursos asignados
- ✅ Lista de alumnos por curso
- ✅ Gestión de notas (3 parciales)
- ✅ Cálculo automático de nota final
- ✅ Comentarios y observaciones

### Alumno
- ✅ Dashboard personalizado
- ✅ Visualización de todas las notas
- ✅ Consulta por curso específico
- ✅ Seguimiento del rendimiento

## 🎨 Interfaz de Usuario

- **Diseño responsive** que se adapta a móviles y tablets
- **Bootstrap 5** para componentes modernos
- **Iconos Font Awesome** para mejor UX
- **Colores semánticos** para estados de notas
- **Navegación intuitiva** por roles

## 🔧 Personalización

### Cambiar Configuración de Base de Datos

Editar `app/__init__.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://usuario:contraseña@localhost/nombre_bd'
```

### Modificar Estilos

Los estilos personalizados están en `app/static/main/styles/sistema.css`

### Agregar Nuevas Funcionalidades

1. Crear nuevo blueprint en `app/modules/`
2. Registrar en `app/routes.py`
3. Crear templates correspondientes

## 🐛 Solución de Problemas

### Error de Conexión a Base de Datos
- Verificar que MySQL esté ejecutándose
- Comprobar credenciales en `app/__init__.py`
- Asegurar que la base de datos existe

### Error de Importación
- Verificar que todas las dependencias estén instaladas
- Activar el entorno virtual correctamente

### Problemas de Permisos
- Verificar que el usuario tenga permisos en la base de datos
- Comprobar la configuración de MySQL

## 📞 Soporte

Para soporte técnico o reportar problemas:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo

## 📄 Licencia

Este proyecto está desarrollado para el Instituto Superior Tecnológico Público Suiza.

---

**Desarrollado con ❤️ para la educación tecnológica**