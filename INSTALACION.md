# 🚀 Instalación Rápida - Sistema de Gestión de Notas

## Requisitos Previos

- ✅ Python 3.8 o superior
- ✅ MySQL 5.7+ o MariaDB 10.3+
- ✅ XAMPP (recomendado para desarrollo)

## Instalación Rápida (Recomendado)

### 🚀 Instalación Automática
```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Ejecutar instalación automática
python install_complete.py
```

### 📋 Instalación Manual (Si la automática falla)

#### 1️⃣ Preparar Base de Datos
- Iniciar XAMPP o MySQL
- Crear base de datos: `sistema_academico`

#### 2️⃣ Instalar Dependencias
```bash
pip install -r requirements.txt
```

#### 3️⃣ Probar Conexión
```bash
python simple_test.py
```

#### 4️⃣ Inicializar Sistema
```bash
python init_db.py
```

#### 5️⃣ Ejecutar Aplicación
```bash
python app.py
```

🌐 **Acceder a:** http://localhost:5000

## 🔧 Configuración Avanzada

### Variables de Entorno
Crear archivo `.env`:
```env
FLASK_ENV=development
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=sistema_academico
SECRET_KEY=tu_clave_muy_segura
```

### Configuración de Producción
```bash
export FLASK_ENV=production
python app.py
```

## 🎯 Primeros Pasos

1. **Iniciar sesión como Administrador**
   - DNI: `12345678`
   - Contraseña: `admin123`

2. **Crear más usuarios**
   - Ir a "Docentes" → "Registrar Docente"
   - Ir a "Alumnos" → "Registrar Alumno"

3. **Gestionar cursos**
   - Ir a "Cursos" → "Registrar Curso"
   - Asignar cursos a docentes
   - Matricular alumnos

4. **Probar funcionalidades**
   - Iniciar sesión como docente
   - Gestionar notas de alumnos
   - Iniciar sesión como alumno
   - Ver calificaciones

## 🐛 Solución de Problemas

### Error: "AmbiguousForeignKeysError" al hacer login
```bash
# Ejecutar diagnóstico
python debug_login.py

# Si el diagnóstico falla, reinstalar dependencias
pip uninstall -y Flask-SQLAlchemy SQLAlchemy mysql-connector-python
pip install -r requirements.txt

# Recrear base de datos
python init_db.py
```

### Error: "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Error: "Can't connect to MySQL"
- Verificar que MySQL esté ejecutándose
- Comprobar credenciales en `config.py`
- Probar conexión: `python test_db.py`

### Error: "Table doesn't exist"
```bash
python init_db.py
```

### Puerto 5000 ocupado
```bash
# Cambiar puerto en app.py
app.run(debug=True, port=5001)
```

### Error de importación de modelos
```bash
# Verificar que no haya archivos .pyc
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Reinstalar dependencias
pip install --force-reinstall -r requirements.txt
```

## 📱 Acceso Móvil

El sistema es completamente responsive:
- 📱 Móviles
- 📱 Tablets
- 💻 Escritorio

## 🔐 Seguridad

- ✅ Autenticación por roles
- ✅ Contraseñas encriptadas
- ✅ Sesiones seguras
- ✅ Validación de datos

## 📞 Soporte

Si tienes problemas:
1. Revisar este archivo
2. Consultar README.md completo
3. Crear issue en el repositorio

---

**¡Listo! Tu sistema de gestión de notas está funcionando** 🎉
