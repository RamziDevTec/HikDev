HikDev - Kameraüberwachung mit intelligentem Personenzähler für smarte individuelle Aktionen



Ein Python-basiertes Tool zur Personenerkennung mit der Hikvision-Kamera (Modell: DS-2CD234G2-ISU/SL). Erkennt Personen live und löst abhängig von der Anzahl gezielt eine Aktion aus. Vordefiniert ist ein Alarmausgang für extern verbundene Geräte wie Lichter, Sirenen etc.



Features

 	•	KI-basierter Personenzähler

 	•	Selbstgeschriebene Funktionen können als Aktionen genutzt werden

 	•	Anleitung für die Konfiguration über die Weboberfläche der Kamera

 	•	Ausführbar als Python-Datei, .exe-Datei oder Windows-Dienst





**Installation Windows:**



Zip-Datei per GUI entpacken in z.B. C:\\Program Files\\HikDev





**Installation Linux (Ubuntu CLI):**



Entweder per SCP von einem Windows übertragen:

 	•	In der Windows PowerShell: "scp \[Pfad zu HikDev.tar.gz] \[ubuntuuser]@\[ubuntu-ip]:/home/\[ubuntuuser]/" für eine Übertragung. Dafür müssen beide Geräte im gleichen Netzwerk sein.



Oder per USB-Stick übertragen.



Dann im Linux-Terminal entpacken mit: "tar -xzf HikDev.tar.gz", anschließend kann die HikDev.tar.gz-Datei gelöscht werden.



Mit "nano HikDev/README.md" im Terminal kann die README gelesen werden. Es ist allerdings empfohlen dies auf einem Gerät mit grafischer Oberfläche zu öffnen.

