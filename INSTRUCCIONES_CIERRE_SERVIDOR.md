# 🔌 Instrucciones para Cerrar el Servidor

## 📋 Problema Resuelto

Antes, cuando cerrabas el navegador, el proceso del servidor seguía activo en segundo plano. Ahora tienes **3 formas** de cerrar el servidor correctamente.

---

## ✅ Soluciones Implementadas

### 1️⃣ **Ícono en la Bandeja del Sistema (System Tray)** ⭐ RECOMENDADO

Cuando ejecutas el `.exe`, aparece un ícono en la bandeja del sistema (junto al reloj).

**Cómo usar:**
1. Busca el ícono azul en la bandeja del sistema (abajo a la derecha)
2. Haz **clic derecho** sobre el ícono
3. Selecciona **"Salir"**
4. El servidor se cerrará completamente

**Opciones del menú:**
- **Abrir en Navegador**: Abre la aplicación en una nueva pestaña
- **Salir**: Cierra el servidor completamente

---

### 2️⃣ **Botón "Apagar Servidor" en el Panel de Administración**

Solo disponible para usuarios con rol de **Administrador**.

**Cómo usar:**
1. Inicia sesión como administrador
2. En el menú lateral, busca el botón **"Apagar Servidor"** (en rojo, al final del menú)
3. Haz clic en el botón
4. Confirma que deseas apagar el servidor
5. El servidor se cerrará automáticamente

---

### 3️⃣ **Administrador de Tareas** (Método manual)

Si por alguna razón no puedes usar las opciones anteriores:

1. Abre el **Administrador de Tareas** (Ctrl + Shift + Esc)
2. Busca el proceso **"SistemaNotas.exe"**
3. Haz clic derecho → **Finalizar tarea**

---

## 🔧 Instalación de Dependencias

Antes de compilar, instala la nueva dependencia:

```cmd
pip install pystray==0.19.5
```

O instala todas las dependencias actualizadas:

```cmd
pip install -r requirements.txt
```

---

## 📦 Compilación

Para compilar el ejecutable con las nuevas funcionalidades:

```cmd
build_exe.bat
```

---

## 🧪 Pruebas

### Probar el ícono de la bandeja del sistema:

```cmd
python test_system_tray.py
```

Esto abrirá el ícono en la bandeja para verificar que se carga correctamente.

### Probar el botón Reintentar del Splash Screen:

```cmd
python test_splash_retry.py
```

### Probar el servidor en modo desarrollo:

```cmd
python run_server_new.py
```

En modo desarrollo:
- **NO** aparece el ícono en la bandeja del sistema
- **SÍ** funciona el botón "Apagar Servidor" en el panel de admin
- Puedes cerrar con **Ctrl + C** en la consola

---

## 📝 Notas Importantes

### Ícono en la Bandeja del Sistema:
- Solo aparece cuando ejecutas el **`.exe`** (modo producción)
- **NO** aparece en modo desarrollo (`python run_server_new.py`)
- El ícono es el **mismo logo del ejecutable** (logo-dsi.ico)

### Botón "Apagar Servidor":
- Solo visible para usuarios con rol **Administrador**
- Funciona tanto en modo desarrollo como en el ejecutable
- Cierra el servidor de forma elegante

### Seguridad:
- La ruta `/shutdown` requiere autenticación
- Solo los administradores pueden apagar el servidor
- Se muestra una confirmación antes de apagar

---

## 🎯 Flujo Recomendado

### Para Usuarios Finales (Ejecutable):

1. **Iniciar**: Doble clic en `SistemaNotas.exe`
2. **Usar**: Trabaja normalmente en el navegador
3. **Cerrar**: Clic derecho en el ícono de la bandeja → Salir

### Para Desarrolladores:

1. **Iniciar**: `python run_server_new.py`
2. **Usar**: Trabaja normalmente
3. **Cerrar**: Ctrl + C en la consola

---

## ❓ Preguntas Frecuentes

**P: ¿Por qué no veo el ícono en la bandeja del sistema?**
R: El ícono solo aparece cuando ejecutas el `.exe`. En modo desarrollo no se muestra.

**P: ¿Puedo cerrar el navegador sin cerrar el servidor?**
R: Sí, el servidor seguirá corriendo. Puedes volver a abrir el navegador y acceder a `http://127.0.0.1:5000/`

**P: ¿Qué pasa si cierro el navegador y quiero volver a entrar?**
R: Simplemente abre el navegador y ve a `http://127.0.0.1:5000/` o haz clic derecho en el ícono de la bandeja → "Abrir en Navegador"

**P: ¿El botón "Apagar Servidor" cierra solo mi sesión o todo el servidor?**
R: Cierra **TODO** el servidor. Todos los usuarios conectados perderán acceso.

**P: ¿Puedo usar el sistema sin cerrar el servidor entre sesiones?**
R: Sí, puedes dejar el servidor corriendo y solo cerrar sesión en el navegador.

---

## 🐛 Solución de Problemas

### El ícono no aparece en la bandeja:
1. Verifica que estés ejecutando el `.exe` (no el script Python)
2. Revisa la bandeja del sistema (puede estar oculto en "Mostrar iconos ocultos")
3. Reinstala la dependencia: `pip install pystray==0.19.5`
4. Verifica que el archivo `logo-dsi.ico` exista en `app/static/main/assets/img/`

### El botón "Apagar Servidor" no funciona:
1. Verifica que estés logueado como **Administrador**
2. Revisa la consola del navegador (F12) para ver errores
3. Verifica que la ruta `/shutdown` esté disponible

### El servidor no se cierra:
1. Usa el Administrador de Tareas como último recurso
2. Verifica que no haya múltiples instancias corriendo
3. Reinicia el equipo si es necesario

---

## 📚 Archivos Modificados

- ✅ `splash_screen.py` - Botón Reintentar funcional
- ✅ `system_tray.py` - Nuevo: Ícono en bandeja del sistema
- ✅ `run_server_new.py` - Integración del system tray
- ✅ `app/modules/main/routes.py` - Ruta `/shutdown`
- ✅ `app/templates/admin/base_admin.html` - Botón "Apagar Servidor"
- ✅ `requirements.txt` - Dependencia `pystray`

---

**¡Listo!** Ahora tienes control completo sobre el servidor 🎉
