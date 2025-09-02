@echo off

echo [INFO] Umgebung aktivieren...
call .venv\Scripts\activate.bat

echo [INFO] Baue EXE...
pyinstaller --onefile --noconsole --name HikDev --distpath . --icon="icon.ico" app.py

pause