# 📦 Guía de Compilación del Ejecutable

## 🚀 Compilación Rápida

```cmd
# 1. Compilar (espera 5-10 minutos)
build_exe.bat

# 2. Probar
cd dist
SistemaNotas.exe
```

---

## ✨ Funcionalidades Implementadas

### 1. Sistema de Logs
- **Ruta**: `/admin/logs`
- Visualización, filtrado y descarga de logs
- Compatible con ejecutable (rutas dinámicas)

### 2. Optimización de Logos
- Conversión automática a base64
- Almacenamiento en base de datos
- Sin archivos externos

### 3. Splash Screen
- Pantalla de carga profesional
- Progreso en tiempo real
- Manejo visual de errores

---

## 📋 Requisitos

### Sistema
- Windows 7+
- XAMPP con MySQL

### Configuración (.env)
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=sistema_academico
SECRET_KEY=tu_clave_secura
```

---

## 📁 Estructura

### Después de compilar:
```
📁 dist/
  ├── SistemaNotas.exe
  └── .env
```

### Al ejecutar (se crea automáticamente):
```
📁 dist/
  ├── SistemaNotas.exe
  ├── .env
  └── 📁 logs/
      └── app.log
```

---

## 🐛 Solución de Problemas

| Problema | Solución |
|----------|----------|
| "No se pudo conectar a MySQL" | Inicia MySQL en XAMPP |
| "Credenciales incorrectas" | Verifica `DB_USER` y `DB_PASSWORD` en `.env` |
| "No se encuentra .env" | Copia `.env` a la carpeta `dist/` |

---

## 👤 Usuarios por Defecto

| Rol | Email | Contraseña |
|-----|-------|------------|
| Admin | admin@sistema.edu | admin123 |
| Docente | juan.perez@sistema.edu | docente123 |
| Alumno | maria.gonzalez@sistema.edu | alumno123 |

---

## ✅ Verificación

Después de ejecutar el .exe:

- [ ] Splash screen aparece
- [ ] Navegador se abre automáticamente
- [ ] Login funciona
- [ ] Panel de logs accesible en `/admin/logs`
- [ ] Carpeta `logs/` se crea automáticamente
