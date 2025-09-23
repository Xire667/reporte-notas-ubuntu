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

- Python 3.8+
- MySQL 5.7+ o MariaDB 10.3+
- XAMPP (recomendado para desarrollo)

## 🔧 Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd reporte-notas-ubuntu
```

### 2. Crear entorno virtual
```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
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

Editar `app/__init__.py` y actualizar la configuración de la base de datos:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://usuario:contraseña@localhost/sistema_academico'
```

### 6. Ejecutar la aplicación
```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

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
├── app.py                       # Punto de entrada de la aplicación
├── requirements.txt             # Dependencias de Python
└── README.md                    # Este archivo
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