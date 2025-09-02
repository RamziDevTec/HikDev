HikDev - Kameraüberwachung mit intelligentem Personenzähler für smarte individuelle Aktionen



Ein Python-basiertes Tool zur Personenerkennung mit der Hikvision-Kamera (Modell: DS-2CD234G2-ISU/SL). Erkennt Personen live und löst abhängig von der Anzahl gezielt eine Aktion aus. Vordefiniert ist ein Alarmausgang für extern verbundene Geräte wie Lichter, Sirenen etc.



Features

 	•	KI-basierter Personenzähler

 	•	Selbstgeschriebene Funktionen können als Aktionen genutzt werden

 	•	Anleitung für die Konfiguration über die Weboberfläche der Kamera

 	•	Ausführbar als Python-Datei, .exe-Datei oder Windows-Dienst





**Einrichtung Windows:**



1\. Projekt herunterladen



Zip-Datei entpacken in z. B. C:\\Program Files\\HikDev





2\. Python 3.10.0 installieren:



Download: https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe

 	•	Bei der Installation “Add Python to PATH” aktivieren

 	•	PIP mit installieren



3\. Konfiguration



config.xml öffnen und konfigurieren. Wichtige Parameter:

 	•	cameraIp (falls onlyCameraAccess aktiv ist)

 	•	hikvisionLogin-Daten

 	•	baseDir-Pfad



4\. Es gibt ein Problem mit einer Bibliothek namens "PyInstaller" für Python 3.10 bei der Erstellung einer EXE-Datei. Lösung:

 	1.	Windows + R → %appdata% eingeben → AppData

 	2.	Navigieren und öffnen: Local\\Programs\\Python\\Python310\\Lib\\dis.py

 	3.	"def \_unpack\_opargs(code):" suchen, else-Block ersetzen durch (Auf die Einrückungen achten):



else:

    arg = None

    extended\_arg = 0

yield (i, op, arg)



Dabei unbedingt auf unsichtbare Leerzeichen achten! Diese werden z.B. in VSCode gezeigt. Sonst kann keine Umgebung erstellt werden.



5\. Python-Umgebung erstellen:

venv-setup.bat ausführen

 	•	Erstellt eine Python-Umgebung und installiert alle nötigen Abhängigkeiten.

 	•	Jetzt kann die Python-Datei "app.py" auf der gewünschten Plattform ausgeführt werden.





6\. (Optional) Exe-Datei erstellen:



exe-setup.bat ausführen

 	•	Erst nach erfolgreicher Kamerakonfiguration funktionstüchtig

 	•	Erstellt eine HikDev.exe, die im Hintergrund laufen kann. Im Task-Manager beenden möglich.



7\. (Optional) Dienst einrichten:

 	•	PowerShell als Admin öffnen

 	•	Ordner wechseln (Pfad angeben): cd "Pfad\\Zu\\HikDev"

 	•	Skript ausführen: ./service-setup.ps1

 	•	Bei Fehlermeldung: "Set-ExecutionPolicy ByPass -Scope Process" eingeben und mit "J" bestätigen

 	•	Dienst heißt hikdev-svc und kann in "Dienste" von Windows überprüft werden





Bemerkungen:

 	Wird der Ordner verschoben oder umbenannt, muss exe-setup.bat erneut ausgeführt werden. Vorher folgende Dateien/Ordner löschen:

 	1.	.venv

 	2.	build

 	3.	HikDev.exe

 	4.	HikDev.spec



Dann: venv-setup.bat, exe-setup.bat und ggf. service-setup.ps1 erneut ausführen.







**Einrichtung Linux (Ubuntu):**



1\. Projekt herunterladen



Entweder per SCP von einem Windows übertragen:

 	•	In der Windows PowerShell: "scp \[Pfad zu HikDev.tar.gz] \[ubuntuuser]@\[ubuntu-ip]:/home/\[ubuntuuser]/" für eine automatisierte Installation. Dafür müssen beide Geräte im gleichen Netzwerk sein.



Oder per USB-Stick übertragen.



Dann im Linux-Terminal entpacken mit: "tar -xzf HikDev.tar.gz", anschließend kann die HikDev.tar.gz-Dateie gelöscht werden.



Mit "nano HikDev/README.md" im Terminal kann die README gelesen werden. Es ist allerdings empfohlen dies auf einem Gerät mit grafischer Oberfläche zu öffnen.



2\. Python 3.10.0 installieren:



Download-Python ausführen:

 	•	In der CLI: "cd /home/\[ubuntuuser]/HikDev" um auf den Ordner zuzugreifen.

 	•	In der CLI: "bash download-python.sh" eingeben für eine automatisierte Installation. Das könnte ein paar Minuten dauern.





3\. Konfiguration



config.xml öffnen und konfigurieren:

 	•	Im Ordner in der CLI: "nano config.xml" um die Datei zu bearbeiten. Zum Speichern und verlassen "Strg + O" dann "Strg + X".



4\. Python-Umgebung erstellen:

venv-setup.sh ausführen

 	•	Im Ordner in der CLI: "bash venv-setup.sh" eingeben. Erstellt eine Python-Umgebung und installiert alle nötigen Abhängigkeiten.



6\. Programm starten:



app.py ausführen (nach der Kamera-Konfiguration):

 	•	Stelle sicher, dass die venv (Python-Umgebung) aktiviert ist. Das ist zu erkennen, wenn in der CLI vor "user@ubuntu-server:~/HikDev$" ein "(.venv)" steht. Falls nicht:

 		•	Im Ordner in der CLI: "source .venv/bin/activate"

 	•	Im Ordner in der CLI: "python3.10 app.py" eingeben.







**Konfiguration der Kamera:**

 	1.	IP-Adresse der Kamera herausfinden (z. B. über SADP Tool)

 	2.	Weboberfläche mit der IP-Adresse im Browser öffnen (Beide müssen im gleichen Netzwerk sein)

 	3.	Unter VCA → Smart Ereignis:

 		•	Bereichseingang und Bereichsausgang (Detectie verlaten regio) konfigurieren

 		•	Polygone mit bis zu 10 Ecken möglich (4 Ecken sind unterstützt, sonst nichts). Auswahl beenden mit Rechtsklick nach der vierten Ecke.

 		•	Empfindlichkeit und Zielgültigkeit einstellen:

 		•	“Höchste” = nur direkt auf Linie

 		•	“Basis” = auch nahe der Linie

 	4.	Scharfschaltungszeitplan \& Verknüpfungsmethoden:

 		•	Audioverknüpfung: spielt Ton ab (nicht HikDev-kompatibel)

 		•	E-Mail senden: E-Mail mit Bild

 		•	Notrufzentrale benachrichtigen (WICHTIG):

 			•	Sendet POST an den HikDev-Server

 			•	In den Einstellungen unter Ereignis/Alarmeinstellungen/Alarmserver Server hinzufügen:

 			•	Die in der config.xml angegebene HOST\_IP als Ziel-IP angeben

 			•	URL: /alarm, Protokolltyp: HTTP, Port = wie in config.xml (Standard: 5000)

 		•	FTP/Speicherkarte/NAS: Für das Speichern (nicht HikDev-kompatibel)

 		•	Lichtblitz Alarm: aktiviert Kamera-Blitz (nicht HikDev-kompatibel)

 		•	Alarmausgang auslösen (WICHTIG): HikDev sendet Stromsignal. Für alle externen Geräte.

 		•	Aufnahmeverknüpfung: startet Kameraaufnahme bei Ereignis



Wichtig: Nach jeder Änderung speichern, sonst gehen Einstellungen verloren!



HikDev unterstützt kein FTP o.ä., nur HTTP-basierte Verbindungen.





Fertig! HikDev ist jetzt einsatzbereit.

