@echo off
setlocal

REM Opcional: activar venv si existe (prioriza venv311)
IF EXIST "venv311\Scripts\activate.bat" (
  call "venv311\Scripts\activate.bat"
) ELSE IF EXIST "venv\Scripts\activate.bat" (
  call "venv\Scripts\activate.bat"
)

REM Generar icono multiresolución desde PNG
python tools\generate_ico.py

REM Generar ejecutable (one-file) incluyendo plantillas, estáticos y .env
pyinstaller --noconfirm --clean --onefile --log-level INFO ^
  --add-data "app/templates;app/templates" ^
  --add-data "app/static;app/static" ^
  --add-data ".env;." ^
  --icon "app\\static\\main\\assets\\img\\logo-dsi.ico" ^
  --collect-all mysql.connector ^
  --collect-all sqlalchemy ^
  --collect-all jinja2 ^
  --hidden-import dotenv ^
  --hidden-import flask_login ^
  --hidden-import xhtml2pdf ^
  --hidden-import reportlab ^
  --hidden-import openpyxl ^
  --hidden-import waitress ^
  --name "SistemaNotas" run_server.py

echo.
echo Ejecutable generado en: dist\SistemaNotas.exe
echo Recuerda encender XAMPP y MySQL antes de ejecutar el .exe
echo.
endlocal