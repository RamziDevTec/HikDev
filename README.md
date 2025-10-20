# HikDev - Kameraüberwachung mit intelligentem Personenzähler als Erweiterung eines Gates

Ein Python-basiertes Tool zur Personenerkennung mit der Hikvision-Kamera (Modell: **DS-2CD234G2-ISU/SL**). Erkennt Personen live und löst abhängig von der Anzahl gezielt eine Aktion aus.  
Grundsätzlich fungiert HikDev als Erweiterung eines Gates für personallose Fitness-Studios. So kann man das sogenannte **"Tailgating"** (unbefugtes Miteintreten mehrerer Personen durch die Türöffnung eines Chips/Codes) verhindern.

---

## Features
- KI-basierter Personenzähler (Yolo v11)
- Kompatibel mit Hikvision-Kameras
- Kompatibel mit Gates
- Anleitung für die Konfiguration über die Weboberfläche der Kamera
- Optimiert für Windows als Python-Skript, EXE-Anwendung und Dienst, aber auch für Linux (Ubuntu/Debian) als Python-Skript oder systemd-Service

---

## Einrichtung Windows

1. **Projekt herunterladen**  
   Zip-Datei entpacken in z. B. `C:\Program Files\HikDev`

2. **Python 3.10.0 installieren**  
   Download: [Python 3.10.0 (64-bit)](https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe)  
   - Bei der Installation **“Add Python to PATH”** aktivieren  
   - **PIP** mit installieren  

3. **Konfiguration**  
   `config.xml` öffnen und konfigurieren. Wichtige Parameter:
   - `cameraIp` (falls `onlyCameraAccess` aktiv ist)
   - `hikvisionLogin`-Daten
   - `baseDir`-Pfad

4. **Python-Umgebung erstellen**  
   `venv-setup.bat` ausführen:
   - Erstellt eine Python-Umgebung und installiert alle nötigen Abhängigkeiten (kann ein paar Minuten dauern).
   - Jetzt kann die Python-Datei `app.py` auf der gewünschten Plattform ausgeführt werden.
   - Stelle sicher, dass die **venv (Python-Umgebung)** aktiviert ist. Das ist zu erkennen, wenn in der CLI vor alles andere ein `(.venv)` steht.  
     Falls nicht:
     ```powershell
     ..venv\Scripts\Activate.ps1
     ```
     Danach Skript starten.

5. **Problem mit PyInstaller bei Python 3.10 (nur bei EXE-Erstellung)**  
   - `Win + R` → `%appdata%` eingeben → Ordner `AppData` öffnen  
   - Navigieren: `Local\Programs\Python\Python310\Lib\dis.py`  
   - Funktion `def _unpack_opargs(code):` suchen  
   - Den `else`-Block ersetzen durch:
     ```python
     else:
         arg = None
         extended_arg = 0
     yield (i, op, arg)
     ```
     Achtung: auf Einrückungen und unsichtbare Leerzeichen achten (z. B. in VSCode sichtbar).  

6. **(Optional) Exe-Datei erstellen**  
   `exe-setup.bat` ausführen:
   - Erst nach erfolgreicher Kamerakonfiguration funktionstüchtig
   - Erstellt eine `HikDev.exe`, die im Hintergrund laufen kann (im Task-Manager beendbar)

7. **(Optional) Dienst einrichten**  
   - PowerShell als Admin öffnen  
   - Ordner wechseln:
     ```powershell
     cd "Pfad\Zu\HikDev"
     ```
   - Skript ausführen:
     ```powershell
     ./service-setup.ps1
     ```
   - Falls Fehlermeldung:  
     ```powershell
     Set-ExecutionPolicy ByPass -Scope Process
     ```
     und mit `J` bestätigen  
   - Dienst heißt `hikdev-svc` und kann in den Windows-Diensten überprüft werden  

### Bemerkungen
Wird der Ordner verschoben oder umbenannt, muss `exe-setup.bat` erneut ausgeführt werden.  
Vorher folgende Dateien/Ordner löschen:
1. `.venv`
2. `build`
3. `HikDev.exe`
4. `HikDev.spec`

Dann: `venv-setup.bat`, `exe-setup.bat` und ggf. `service-setup.ps1` erneut ausführen.

---

## Einrichtung Linux (Ubuntu)

1. **Projekt herunterladen**
   - Per SCP von Windows übertragen:
     ```powershell
     scp [Pfad zu HikDev.tar.gz] [ubuntuuser]@[ubuntu-ip]:/home/[ubuntuuser]/
     ```
     (beide Geräte müssen im gleichen Netzwerk sein)  
   - Oder per USB-Stick übertragen  
   - Entpacken:
     ```bash
     tar -xzf HikDev.tar.gz
     ```
     Danach kann `HikDev.tar.gz` gelöscht werden.  

   - README öffnen:
     ```bash
     nano HikDev/README.md
     ```
     (Empfohlen: auf einem Gerät mit GUI öffnen)

2. **Python 3.10.0 installieren**
   - In den Projektordner wechseln:
     ```bash
     cd /home/[ubuntuuser]/HikDev
     ```
   - Script starten:
     ```bash
     bash download-python.sh
     ```

3. **Konfiguration**
   - Datei öffnen:
     ```bash
     nano config.xml
     ```
   - Änderungen speichern: `Strg + O`, dann `Strg + X`

4. **Python-Umgebung erstellen**
   - Script ausführen:
     ```bash
     bash venv-setup.sh
     ```
   - Falls Abbruch mit *No space left on Device*:
     ```bash
     bash no-space.sh
     ```

6. **Programm starten**
   - venv aktivieren:
     ```bash
     source .venv/bin/activate
     ```
   - App starten:
     ```bash
     python3.10 app.py
     ```

7. **Als Linux Service starten**
   - Script starten:
     ```bash
     bash systemd-service-setup.sh
     ```
   - Status prüfen:
     ```bash
     sudo systemctl status hikdev
     ```
   - Log ansehen:
     ```bash
     journalctl -u hikdev -f
     ```
   - Stoppen:
     ```bash
     sudo systemctl stop hikdev
     ```
   - Deaktivieren:
     ```bash
     sudo systemctl disable hikdev
     ```
   - Löschen:
     ```bash
     sudo rm /etc/systemd/system/hikdev.service
     ```

---

## Konfiguration der Kamera

1. IP-Adresse der Kamera herausfinden (z. B. über SADP Tool)
2. Weboberfläche mit der IP im Browser öffnen (beide Geräte müssen im gleichen Netzwerk sein)
3. Unter **VCA → Smart Ereignis**:
   - Bereichseingang und -ausgang konfigurieren
   - Polygone mit bis zu 10 Ecken möglich (HikDev unterstützt max. 4)
   - Empfindlichkeit einstellen:
     - **Höchste** = nur direkt auf Linie
     - **Basis** = auch nahe der Linie
4. **Scharfschaltungszeitplan & Verknüpfungsmethoden**
   - Audioverknüpfung → spielt Ton ab (nicht HikDev-kompatibel)
   - E-Mail senden → E-Mail mit Bild
   - Notrufzentrale benachrichtigen (**WICHTIG**):
     - Sendet POST an den HikDev-Server
     - Einstellungen → Ereignis → Alarmeinstellungen → Alarmserver hinzufügen:
       - Ziel-IP = `HOST_IP` aus `config.xml`
       - URL: `/alarm`
       - Protokolltyp: HTTP
       - Port = wie in `config.xml` (Standard: 5000)
   - FTP / NAS / Speicherkarte → Speicherung (nicht HikDev-kompatibel)
   - Lichtblitz Alarm → aktiviert Kamera-Blitz (nicht HikDev-kompatibel)
   - Alarmausgang auslösen (**WICHTIG**) → HikDev sendet Stromsignal an externe Geräte
   - Aufnahmeverknüpfung → startet Aufnahme bei Ereignis

⚠️ **Wichtig:** Nach jeder Änderung speichern, sonst gehen Einstellungen verloren!  
HikDev unterstützt **nur HTTP-basierte Verbindungen**, kein FTP o. ä.

---

✅ **Fertig! HikDev ist jetzt einsatzbereit.**
