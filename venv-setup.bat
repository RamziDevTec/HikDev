@echo off

echo [INFO] Virtuelle Umgebung wird erstellt...
python -m venv .venv

echo [INFO] Umgebung wird aktiviert...
call .venv\Scripts\activate.bat

echo [INFO] Pip wird aktualisiert...
.venv\Scripts\python.exe -m pip install --upgrade pip

echo [INFO] Abhaengigkeiten werden installiert...
pip install -r requirements.txt


pause