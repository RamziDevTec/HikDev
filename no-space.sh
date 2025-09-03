#!/bin/bash

set -e  # Skript beendet sich bei Fehler

CURRENT_DIR=$(pwd)
# Prüfen, ob .venv existiert und löschen
VENV_DIR="$CURRENT_DIR/.venv"
if [ -d "$VENV_DIR" ]; then
    echo "Lösche virtuelle Umgebung: $VENV_DIR"
    rm -rf "$VENV_DIR"
    echo ".venv wurde gelöscht."
else
    echo "Keine virtuelle Umgebung gefunden."
fi

# TMPDIR auf Home-Partition setzen
TMP_HOME="$HOME/tmp_hikdev"
echo "Erstelle temporären Ordner auf Home-Partition: $TMP_HOME"
mkdir -p "$TMP_HOME"
export TMPDIR="$TMP_HOME"
echo "TMPDIR gesetzt auf: $TMPDIR"

# Starte venv-setup.sh
SETUP_SCRIPT="$CURRENT_DIR/venv-setup.sh"
if [ -f "$SETUP_SCRIPT" ]; then
    echo "Starte venv-setup.sh..."
    bash "$SETUP_SCRIPT"
else
    echo "venv-setup.sh nicht gefunden im Ordner $CURRENT_DIR"
fi
