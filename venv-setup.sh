#!/bin/bash

# Skript stoppt bei Fehlern
set -e

echo "[INFO] Virtuelle Umgebung wird erstellt..."
python3.10 -m venv .venv

echo "[INFO] Umgebung wird aktiviert..."
source .venv/bin/activate

echo "[INFO] Pip wird aktualisiert..."
python -m pip install --upgrade pip

echo "[INFO] Abhängigkeiten werden installiert..."
pip install -r requirements-l.txt


echo "[INFO] Fertig!"
