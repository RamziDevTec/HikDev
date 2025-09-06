#!/bin/bash

# Variablen anpassen
USER_NAME="devtec"
HIKDEV_DIR="/home/devtec/HikDev"
PYTHON_BIN="$HIKDEV_DIR/.venv/bin/python3.10"
SERVICE_NAME="hikdev"

echo "[INFO] HikDev systemd-Service Setup vorbereiten..."

# Wrapper für sudo
run_cmd() {
    if command -v sudo >/dev/null 2>&1; then
        sudo "$@"
    else
        "$@"
    fi
}

# Prüfen, ob systemd läuft
if ! pidof systemd >/dev/null; then
    echo "[FEHLER] Dieses System verwendet kein systemd!"
    echo "[HINWEIS] Bitte manuell einen Service für Ihr Init-System (z. B. SysVinit) anlegen."
    exit 1
fi

# Prüfen ob Service-Datei existiert
if [ -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
    echo "[INFO] Service-Datei existiert bereits. Wird überschrieben..."
    run_cmd rm -f /etc/systemd/system/$SERVICE_NAME.service
fi

# Service-Datei erstellen
echo "[INFO] Erstelle systemd-Service-Datei..."
run_cmd tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOL
[Unit]
Description=HikDev Hintergrundservice
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$HIKDEV_DIR
ExecStart=$PYTHON_BIN $HIKDEV_DIR/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

# systemd neu laden
echo "[INFO] systemd daemon neu laden..."
run_cmd systemctl daemon-reload

# Service starten
echo "[INFO] Starte Service..."
run_cmd systemctl start $SERVICE_NAME

# Service aktivieren
echo "[INFO] Aktiviere Service beim Boot..."
run_cmd systemctl enable $SERVICE_NAME

# Status anzeigen
echo "[INFO] Service Status:"
run_cmd systemctl status $SERVICE_NAME --no-pager

echo "[INFO] Setup abgeschlossen!"
echo "[HINWEIS] Logs live anzeigen mit: journalctl -u $SERVICE_NAME -f"
