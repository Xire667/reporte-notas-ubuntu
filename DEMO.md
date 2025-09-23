# 🎬 Demostración del Sistema de Gestión de Notas

## 📋 Flujo de Trabajo Completo

### 1️⃣ Acceso Inicial
- **URL:** http://localhost:5000
- **Página de inicio** con información del sistema
- **Botones de acceso** para cada rol

### 2️⃣ Administrador (DNI: 12345678, Contraseña: admin123)

#### Dashboard Administrativo
- 📊 **Estadísticas generales**
  - Total de docentes registrados
  - Total de alumnos registrados
  - Total de cursos activos

#### Gestión de Docentes
- ➕ **Registrar Docente**
  - Formulario con DNI, nombre, apellido, email
  - Contraseña temporal asignada
  - Validación de datos únicos

- 📋 **Lista de Docentes**
  - Tabla con información completa
  - Estados (activo/inactivo)
  - Acciones (ver, editar, activar/desactivar)

#### Gestión de Cursos
- ➕ **Registrar Curso**
  - Código único, nombre, descripción
  - Número de créditos
  - Estado activo/inactivo

- 📋 **Lista de Cursos**
  - Vista completa de todos los cursos
  - Acciones de gestión

#### Asignación de Cursos
- 🔗 **Asignar Cursos a Docentes**
  - Selector de curso
  - Selector de docente
  - Lista de asignaciones actuales

#### Gestión de Alumnos
- ➕ **Registrar Alumno**
  - Formulario similar al docente
  - Rol automático de "alumno"

- 📋 **Lista de Alumnos**
  - Información completa
  - Estados y acciones

#### Matrícula
- 🎓 **Matricular Alumnos**
  - Selector de curso
  - Selector de alumno
  - Lista de matrículas actuales

### 3️⃣ Docente (DNI: 87654321, Contraseña: docente123)

#### Dashboard Docente
- 📚 **Mis Cursos Asignados**
  - Cards con información de cada curso
  - Acceso rápido a gestión de notas
  - Vista de alumnos por curso

#### Gestión de Notas
- 📊 **Gestionar Notas por Curso**
  - Tabla con todos los alumnos del curso
  - Campos para 3 parciales
  - Cálculo automático de nota final
  - Guardado en tiempo real con AJAX

- 👥 **Ver Alumnos del Curso**
  - Lista detallada de estudiantes
  - Información de contacto
  - Acceso a notas individuales

- 📝 **Notas Individuales**
  - Vista detallada por alumno
  - Historial de calificaciones
  - Comentarios y observaciones

### 4️⃣ Alumno (DNI: 11223344, Contraseña: alumno123)

#### Dashboard Alumno
- 👋 **Bienvenida personalizada**
- 📚 **Mis Cursos Matriculados**
  - Cards con información de cursos
  - Acceso directo a notas
  - Estado de calificaciones

#### Visualización de Notas
- 📊 **Todas mis Notas**
  - Tabla completa con todos los cursos
  - Notas por parcial
  - Nota final destacada
  - Códigos de colores (aprobado/regular/desaprobado)

- 📖 **Notas por Curso**
  - Vista detallada de un curso específico
  - Información del curso
  - Historial de calificaciones
  - Comentarios del docente

- 📋 **Mis Cursos**
  - Lista de cursos matriculados
  - Nota final por curso
  - Acceso rápido a detalles

## 🎨 Características de la Interfaz

### Diseño Responsive
- 📱 **Móviles:** Navegación colapsable, cards apiladas
- 📱 **Tablets:** Layout optimizado para pantallas medianas
- 💻 **Escritorio:** Vista completa con sidebar

### Elementos Visuales
- 🎨 **Bootstrap 5** para componentes modernos
- 🎯 **Iconos Font Awesome** para mejor UX
- 🌈 **Colores semánticos** para estados de notas
- ✨ **Animaciones suaves** en transiciones

### Funcionalidades Interactivas
- 🔄 **Actualización en tiempo real** de notas
- 💾 **Guardado automático** con feedback visual
- 🔍 **Búsqueda y filtros** en listas
- 📊 **Cálculos automáticos** de promedios

## 🔐 Sistema de Seguridad

### Autenticación
- 🔑 **Login con DNI y contraseña**
- 👤 **Roles diferenciados** (admin/docente/alumno)
- 🚪 **Logout seguro** con limpieza de sesión

### Autorización
- 🛡️ **Middleware de roles** en cada ruta
- 🔒 **Acceso restringido** según permisos
- ⚠️ **Mensajes de error** informativos

### Validación
- ✅ **Validación de formularios** en frontend y backend
- 🚫 **Prevención de datos duplicados**
- 🔍 **Sanitización de entradas**

## 📊 Gestión de Datos

### Base de Datos
- 🗄️ **MySQL** como motor principal
- 🔗 **SQLAlchemy ORM** para consultas
- 📋 **Relaciones bien definidas** entre entidades

### Modelos Principales
- 👤 **Usuario:** Información personal y autenticación
- 📚 **Curso:** Catálogo de materias
- 🔗 **CursoDocente:** Asignación de cursos
- 🎓 **CursoAlumno:** Matrícula de estudiantes
- 📊 **Nota:** Calificaciones y evaluaciones

## 🚀 Funcionalidades Avanzadas

### Para Administradores
- 📈 **Dashboard con estadísticas**
- 🔄 **Gestión completa de usuarios**
- 📋 **Asignación masiva de cursos**
- 👥 **Matrícula masiva de alumnos**

### Para Docentes
- 📊 **Gestión intuitiva de notas**
- 👥 **Vista de alumnos por curso**
- 💬 **Comentarios y observaciones**
- 📈 **Seguimiento de rendimiento**

### Para Alumnos
- 📊 **Vista clara de calificaciones**
- 🎯 **Seguimiento por curso**
- 📱 **Acceso desde cualquier dispositivo**
- 🔔 **Notificaciones de cambios**

## 🎯 Casos de Uso Típicos

### Escenario 1: Nuevo Semestre
1. Admin crea nuevos cursos
2. Admin registra nuevos docentes
3. Admin asigna cursos a docentes
4. Admin registra nuevos alumnos
5. Admin matricula alumnos en cursos

### Escenario 2: Evaluación Continua
1. Docente accede a sus cursos
2. Docente ve lista de alumnos
3. Docente ingresa notas de parciales
4. Sistema calcula nota final automáticamente
5. Alumno consulta sus calificaciones

### Escenario 3: Consulta de Notas
1. Alumno inicia sesión
2. Alumno ve dashboard con resumen
3. Alumno selecciona curso específico
4. Alumno ve detalle de calificaciones
5. Alumno puede consultar todos sus cursos

## 🔧 Personalización

### Configuración
- ⚙️ **Archivo config.py** para ajustes
- 🌍 **Variables de entorno** para diferentes entornos
- 🎨 **CSS personalizable** en sistema.css

### Extensibilidad
- 🔌 **Arquitectura modular** con blueprints
- 📁 **Estructura clara** para agregar funcionalidades
- 🧩 **Componentes reutilizables**

---

**¡El sistema está listo para usar!** 🎉

Sigue las instrucciones de instalación y comienza a gestionar las notas de tu institución educativa.
