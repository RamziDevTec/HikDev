#!/bin/bash

# Variablen anpassen
USER_NAME="devtec"
HIKDEV_DIR="/home/devtec/HikDev"
PYTHON_BIN="$HIKDEV_DIR/.venv/bin/python3.10"
SERVICE_NAME="hikdev"

echo "=== HikDev systemd-Service Setup ==="

# Prüfen ob Service-Datei existiert
if [ -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
    echo "Service-Datei existiert bereits. Wird überschrieben..."
    sudo rm -f /etc/systemd/system/$SERVICE_NAME.service
fi

# Service-Datei erstellen
echo "Erstelle systemd-Service-Datei..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOL
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
echo "systemd daemon neu laden..."
sudo systemctl daemon-reload

# Service starten
echo "Starte Service..."
sudo systemctl start $SERVICE_NAME

# Service aktivieren
echo "Aktiviere Service beim Boot..."
sudo systemctl enable $SERVICE_NAME

# Status anzeigen
echo "Service Status:"
sudo systemctl status $SERVICE_NAME --no-pager

echo "===== Setup abgeschlossen ====="
echo "Logs live anzeigen mit: journalctl -u $SERVICE_NAME -f"
