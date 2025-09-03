## Warnungen von Torch ignorieren ##
import os
os.environ["TORCH_CPP_LOG_LEVEL"] = "ERROR"

## IMPORTS ##
from flask import Flask, request, abort
import cv2
import numpy as np
import requests
from requests.auth import HTTPDigestAuth
from collections import defaultdict
import string
from datetime import datetime
import time
import threading
import xml.etree.ElementTree as ET
import urllib3#
from ultralytics import YOLO

# Sicherheitswanung deaktivieren. Dadurch entsteht ein lokales Risiko! Allerdings ist es Kostenlos und ein lokaler Angriff würde eine Verbindung auf das interne LAN benötigen.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


## APP-INSTANZ ERSTELLEN ##
app = Flask(__name__)

## KONFIGURATIONSBEREICH ##

#!!---!!#

# Dieser Konfigurationsbereich ist fest im Code verankert (hardcodiert) und wird überschrieben, solange im App-Aufruf die Funktion load_config_from_xml() aktiviert ist – und zwar durch die config.xml-Datei. Andernfalls dienen diese Werte als Standardwerte, falls das Laden der Konfigurationsdatei fehlschlägt.

#!!---!!#

# Zugriff
HTTP_IP = "0.0.0.0" # Wo der HTTP-Server gehostet wird. Normalerweise auf dem eigenen Computer.
HTTP_PORT = "5000" # Port. Standard: "5000"
ONLY_CAMERA_ACCESS = False # Erlaubt nur POSTs von der Kamera.
CAMERA_IP = "0.0.0.0" # IP-Adresse der Kamera. IP der Kamera mit dem SADP-Tool finden.
HIKVISION_LOGIN_USERNAME = "admin" # Benutzername für das Login in der Weboberfläche der Kamera (Hikvision)
HIKVISION_LOGIN_PASSWORD = "password" # Passwort für das Login in der Weboberfläche der Kamera (Hikvision)


# KI
CONFIDENCE_THRESHOLD = 0.7 # Mindestwahrscheinlichkeit für die KI, um Ergebnisse mitzuzählen
MAX_COUNT_TO_ERROR = 10 # Ab wie vielen Personen das Input als Fehler angesehen werden sollte.

# Bilder
SAVE_IMAGES = True # Ob die Bilder gespeichert werden sollen
SAVE_DURATION_HOURS = 48 # Wie viele Stunden die Bilder gespeichert werden sollen. 0 = unendlich.
DEL_INTERVAL_MINUTES = 30 # Nach wie vielen Minuten immer der Bilder-Löscher aktiviert werden sollte 

# Pfade
BASE_DIR = r"C:\Program Files\HikDev" # Pfad zum Hauptordner (ohne Anführungszeichen)
IMAGE_DIR = r"bilder" # Ordner der Bilder

# Entwickler
SHOW_PRINTS = True # Zeigt Print-Befehle für besseres Debuggen (Empfohlen)
INVERT_ALARMOUTPUT = False # Schaltet das Alarmausgang immer an und deaktviert es beim Triggern in result() mit trigger_alarm_output()

## FUNKTIONEN ##
# Konfigurationsfunktion mit config.xml
def load_config_from_xml(path):
    # Holt alle Variablen
    global HTTP_IP, HTTP_PORT, ONLY_CAMERA_ACCESS, CAMERA_IP, HIKVISION_LOGIN_USERNAME, HIKVISION_LOGIN_PASSWORD # Zugriff
    global CONFIDENCE_THRESHOLD, MAX_COUNT_TO_ERROR # KI
    global SAVE_IMAGES, SAVE_DURATION_HOURS, DEL_INTERVAL_MINUTES # Bilder
    global BASE_DIR, IMAGE_DIR # Pfade
    global SHOW_PRINTS, INVERT_ALARMOUTPUT # Entwickler

    try:
        tree = ET.parse(path) # Erstellt aus der config.xml Datei ein Baum
        root = tree.getroot() # intialisiert das root-Element (<config>)

        def gt(key): return root.findtext(key) # Alias für funktion

        HTTP_IP = gt("httpIp")
        HTTP_PORT = gt("httpPort")
        ONLY_CAMERA_ACCESS = gt("onlyCameraAccess").lower() == "true"
        CAMERA_IP = gt("cameraIp")
        HIKVISION_LOGIN_USERNAME = gt("hikvisionLoginUsername")
        HIKVISION_LOGIN_PASSWORD = gt("hikvisionLoginPassword")

        CONFIDENCE_THRESHOLD = float(gt("confidenceThreshold"))
        MAX_COUNT_TO_ERROR = int(gt("max_count_to_error"))

        SAVE_IMAGES = gt("saveImages").lower() == "true"
        SAVE_DURATION_HOURS = float(gt("saveDurationHours"))
        DEL_INTERVAL_MINUTES = float(gt("delIntervalMinutes"))

        BASE_DIR = gt("baseDir")
        IMAGE_DIR = gt("imageDir")

        SHOW_PRINTS = gt("showPrints").lower() == "true"
        INVERT_ALARMOUTPUT = gt("invert_alarmoutput").lower() == "true"

        if SHOW_PRINTS:
            print("===== Konfiguration erfolgreich geladen =====")
    except Exception as e:
        print("Fehler beim Laden der Konfiguration:", e)

# Standart-Konfiguration anzeigen
def print_current_config():
    print("\n===== AKTUELLE KONFIGURATION =====")
    print("(Der Ordner sollte direkt für die Standard-Konfiguration im C-Verzeichnis (C:\hikvision-flask-server) liegen!)")
    print(f"HTTP_IP: {HTTP_IP}")
    print(f"HTTP_PORT: {HTTP_PORT}")
    print(f"ONLY_CAMERA_ACCESS: {ONLY_CAMERA_ACCESS}")
    print(f"CAMERA_IP: {CAMERA_IP}")
    print(f"CONFIDENCE_THRESHOLD: {CONFIDENCE_THRESHOLD}")
    print(f"SAVE_IMAGES: {SAVE_IMAGES}")
    print(f"SAVE_DURATION_HOURS: {SAVE_DURATION_HOURS}")
    print(f"DEL_INTERVAL_MINUTES: {DEL_INTERVAL_MINUTES}")
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"IMAGE_DIR: {IMAGE_DIR}")
    print(f"SHOW_PRINTS: {SHOW_PRINTS}")
    print("===================================\n")

# Falls nur die IP-Adresse der Kamera erlaubt ist: Kontrolliert ob die IP stimmt
def camera_ip_check(ip):
    if ONLY_CAMERA_ACCESS == True and ip != CAMERA_IP:
        return False
    else:
        return True

# Einbruchsbereich aus XML in POST extrahieren
def extract_polygon_from_xml(xml_string):
    try:
        ns = {"hik": "http://www.hikvision.com/ver20/XMLSchema"}
        root = ET.fromstring(xml_string)
        coords = []
        for coord in root.findall(
            ".//hik:DetectionRegionList/hik:DetectionRegionEntry/hik:RegionCoordinatesList/hik:RegionCoordinates",
            ns,
        ):
            x = int(coord.find("hik:positionX", ns).text)
            y = int(coord.find("hik:positionY", ns).text)
            coords.append((x, y))
        return coords
    except Exception as e:
        print("Polygon-Parsing-Fehler:", e)
        return []
    
# Gibt das bild mit maskiertem Einbruchsbereich: Einbruchsbereich, alles andere schwarz
def mask_polygon(image, polygon_coords):
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    if len(polygon_coords) > 0:
        cv2.fillPoly(mask, [np.array(polygon_coords, dtype=np.int32)], 255)
        masked = cv2.bitwise_and(image, image, mask=mask)
        return masked
    else:
        return image  # Kein Polygon → kein Masking

# Bild umwandeln
def convert_img(file):
    img_bytes = file.read() # Liest Bild als Bytes aus
    npimg = np.frombuffer(img_bytes, np.uint8) # Wandelt Bildbytes in NumPy-Array um für OpenCV
    return cv2.imdecode(npimg, cv2.IMREAD_COLOR) # Dekodiert es als Bild im OpenCV-Marix Format (bearbeitbar)

# Bild kleiner skalieren für Perfomance
def resize_image(image, max_width=960, max_height=720):
    h, w = image.shape[:2]
    scale = min(max_width / w, max_height / h)
    if scale < 1.0:  # nur verkleinern, nicht vergrößern
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(image, (new_w, new_h))
    return image

# Kontrolliert ob der Mittelpunkt einer Person im Einbruchsbereich ist
def point_in_polygon(point, polygon):
    contour = np.array(polygon, dtype=np.int32)
    return cv2.pointPolygonTest(contour, point, False) >= 0

def yolo_analysis(image, polygon=None):
    global model # dein YOLO11s Modell (oben geladen)
    # Inferenz mit Ultralytics
    results = model.predict(source=image, verbose=False)[0]

    person_count = 0
    for box in results.boxes:
        cls = int(box.cls[0]) # Klasse (ID) 
        conf = float(box.conf[0]) # Confidence
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        center = (int((x1 + x2) / 2), int((y1 + y2) / 2))

        if cls == 0 and conf > CONFIDENCE_THRESHOLD: # Klasse "Person"
            if polygon is not None and not point_in_polygon(center, polygon):
                continue
            person_count += 1
            label = f"person: {int(conf * 100)}%"
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
    return person_count, image

# Lösung für die Verschiebung des Einbruchsbereichs
def fix_camera_offset(polygon, width, height):
    # Polygon mittig platzieren (von 1000x1000)
    offset_x = 0#(width - 1000) // 2    # = 140 bei 1280px
    offset_y = 0#(1000 - height) // 2   # = 140 bei 720px
    centered = [(x + offset_x, y - offset_y) for (x, y) in polygon] # Verschieben in die Mitte
    scale_x = width / 1000    # = 1.28 stretch
    scale_y = height / 1000   # = 0.72 stretch
    stretched = [(int(x * scale_x), int(y * scale_y)) for (x, y) in centered]
    flipped = [(width - x, height - y) for (x, y) in stretched]
    return flipped

# Polygon bzw. Einbruchsbereich einzeichnen
def draw_polygon(polygon, image):
    pts = np.array(polygon, np.int32)
    pts = pts.reshape((-1,1,2))
    cv2.polylines(image, [pts], isClosed=True, color=(255,0,0), thickness=3)
    for i, point in enumerate(polygon):
        cv2.circle(image, point, 5, (0, 0, 255), -1)
        cv2.putText(image, f"{i+1}", (point[0]+5, point[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)

# Bildbenennung
timestamp_counters = defaultdict(int)
letters = list(string.ascii_lowercase)
def generate_filename(person_count, timestamp):
    timestamp_str = timestamp.strftime('%Y-%m-%d_%H-%M-%S')
    index = timestamp_counters[timestamp_str]
    suffix = letters[index % len(letters)]  # a–z
    timestamp_counters[timestamp_str] += 1
    return os.path.join(BASE_DIR, IMAGE_DIR, f"persons_{person_count}_{timestamp_str}_{suffix}.jpg")

# Bild speichern
def save_img(image, person_count):
    if SAVE_IMAGES:
        timestamp = datetime.now()
        filename = generate_filename(person_count, timestamp)
        cv2.imwrite(filename, image)
        if SHOW_PRINTS:
            print(f"\n===== Bild gespeichert: {filename} =====")
        return filename

# Bilder löschen
def del_old_imgs():
    if SAVE_DURATION_HOURS <= 0: # Überspringt bei 0 SAVE_DURATION_HOURS weil das für die Funktion unendlich bedeutet
        return
    now = datetime.now() # Definiert den aktuellen Zeitpunkt
    cutoff = now.timestamp() - (SAVE_DURATION_HOURS * 3600) # Vergangene Zeit berechnen

    for filename in os.listdir(os.path.join(BASE_DIR, IMAGE_DIR)): # Holt sich alle Namen der Bilder im Bilder-Ordner
        filepath = os.path.join(BASE_DIR, IMAGE_DIR, filename) # Erschafft sich den Pfad des Bildes
        if os.path.isfile(filepath): # Stellt sicher dass es eine Datei ist
            if os.path.getmtime(filepath) < cutoff: # Wenn der Erstellungsdatum kleiner ist als die Vergangene Zeit dann:
                os.remove(filepath) # Löscht das Bild
                if SHOW_PRINTS:
                    print("===== BILD GELÖSCHT: " + filepath + " =====")

# Schleife um Bilder zu löschen. 
def start_del_loop():
    def loop(): # Innere Funktion mt der ganzen Funktionalität
        while True: # Endlos-Schleife
            time.sleep(DEL_INTERVAL_MINUTES * 60) # Wartet die gewählte Interval-Zeit unter DEL_INTERVAL_MINUTES
            del_old_imgs() # Löscht die abgelaufenen Bilder
    thread = threading.Thread(target=loop, daemon=True) # Definiert den Thread zum aktivieren der inneren Funktion
    thread.start() # Startet den Thread und somit die Funktion

# Schalte Strom an dem Alarmausgang
def trigger_alarm_output(trigger:bool):
    try:
        url = f"https://{CAMERA_IP}/ISAPI/System/IO/outputs/1/trigger"
        auth = HTTPDigestAuth(HIKVISION_LOGIN_USERNAME, HIKVISION_LOGIN_PASSWORD)
        headers = {"Content-Type": "application/xml"}
        xml_on = """<?xml version="1.0" encoding="UTF-8"?>
                    <IOPortData xmlns="http://www.hikvision.com/ver20/XMLSchema">
                        <id>1</id>
                        <outputIOPortType>alarmOutPort</outputIOPortType>
                        <outputState>high</outputState>
                    </IOPortData>
                 """ 
        xml_off = xml_on.replace("high", "low")

        aktiviert = "aktiviert"
        deaktiviert = "deaktiviert"
        aktivieren = "aktivieren"
        deaktivieren = "deaktivieren"
        
        if INVERT_ALARMOUTPUT == True: # Invertiert falls erlaubt
            temp = xml_on
            xml_on = xml_off
            xml_off = temp
            aktiviert = "deaktiviert"
            deaktiviert = "aktiviert"
            aktivieren = "deaktivieren"
            deaktivieren = "aktivieren"

        if trigger == True:
            xml_data = xml_on # An
        elif trigger == False:
            xml_data = xml_off # Aus
        else:
            print("===== Interner Fehler im Code (trigger) =====")
            return "===== Interner Fehler im Code (trigger) ====="

        response = requests.put(url, auth=auth, headers=headers, data=xml_data, verify=False) # Sendet Befehl an ISAPI
        #print(response.text) # Für mehr Infos (Standartmäßig auskommentiert)
        if SHOW_PRINTS:
            if response.status_code == 200:
                if trigger:
                    print(f"===== AlarmOutput erfolgreich {aktiviert}: {response.status_code} =====")
                else:
                    print(f"===== AlarmOutput erfolgreich {deaktiviert}: {response.status_code} =====")
            else:
                if trigger:
                    print(f"===== Fehler beim {aktivieren} des AlarmOutputs: {response.status_code} =====")
                else:
                    print(f"===== Fehler beim {deaktivieren} des AlarmOutputs: {response.status_code} =====")

    except Exception as e:
        if SHOW_PRINTS:
            print(f"===== AlarmOutput-Fehler: {e} =====")
        return f"===== AlarmOutput-Fehler: {e} ====="

open_door = False

# Ergebnisse
def result(person_count):
    if person_count >= 2 and person_count < MAX_COUNT_TO_ERROR and open_door:
        if SHOW_PRINTS:
            print(f"\n===== MEHRERE PERSONEN SIND DURCHGEGANGEN: {person_count} =====")
        trigger_alarm_output(False)
        emergency()
        return f"===== MEHRERE PERSONEN SIND DURCHGEGANGEN: {person_count} =====", 200 
    elif person_count >= 2 and person_count < MAX_COUNT_TO_ERROR:
        if SHOW_PRINTS:
            print(f"\n===== MEHRERE PERSONEN ERKANNT: {person_count} =====")
        trigger_alarm_output(False)
        return f"===== MEHRERE PERSONEN ERKANNT: {person_count} =====", 200 
    elif person_count == 1:
        if SHOW_PRINTS:
            print(f"\n===== Eine Person erkannt =====")
        trigger_alarm_output(True)
        return f"===== Eine Person erkannt =====", 200
    elif person_count == 0:
        if SHOW_PRINTS:
            print(f"\n===== Keine Personen erkannt =====")
        trigger_alarm_output(False)
        return f"===== Keine Personen erkannt =====", 200
    else:
        if SHOW_PRINTS:
            print(f"\n===== FEHLSCHLAG ODER {MAX_COUNT_TO_ERROR}+ PERSONEN ERKANNT =====")
            print(f"\n===== KONTROLLIEREN SIE ZUR SICHERHEIT NACH =====")
        trigger_alarm_output(False)
        return f"===== FEHLSCHLAG ODER {MAX_COUNT_TO_ERROR}+ PERSONEN ERKANNT, KONTROLLIEREN SIE ZUR SICHERHEIT NACH =====", 409


def emergency():
    print("===== ALARMMMMMMMMMMMMMMMMMMMMMMMMMMMMM =====")

## YOLO MODELL VORBEREITEN ##
model = YOLO("yolo11s.pt")

## APP ##
@app.route('/alarm', methods=['POST']) # Bei einem POST an /alarm aktiviert sich alarm()
def alarm_handler():
    #print(request.form) # Holt die XML-Datei im POST, standartmäßig auskommentiert
    #print(request.files) # Holt die File-Dateien im POST, standartmäßig auskommentiert

    post_ip = request.remote_addr.split(":")[0] # Speichert die IP-Adresse des Senders
    xml_data = request.form.get("regionEntrance", "") # Einbruchsbereichdaten aus dem POST holen für das Betreten
    if not xml_data: # Falls dieser Einbruchsbereich Ungültig
        xml_data = request.form.get("regionExiting", "") # Einbruchsbereichdaten aus dem POST holen für das Verlassen
    if xml_data:
        polygon = extract_polygon_from_xml(xml_data)
    else: # Sonst holt sich die Einbruchsbereichdaten
        polygon = []
        if SHOW_PRINTS:
            print("POLYGON LEER ODER UNGÜLTIG")
    if SHOW_PRINTS: # Überschrift
        print("\n======== POST an /alarm von:", post_ip , "========")
    if not camera_ip_check(post_ip): # Kontrolliert ob die IP stimmt
        if SHOW_PRINTS:
            print("\n===== ZUGRIFF VERWEIGERT, NICHT ERWARTETE IP-ADRESSE:", post_ip, "=====\n\n======== POST ENDE ========")
        return "Forbidden", 403
    
    # Program #
    try:
        file = request.files.get("regionEnterImage") # Erfragt das Bild für das Betreten im POST mit request
        if not file or file.filename == "": # Falls kein Bild für das Betreten im POST
            file = request.files.get("regionExitImage") # Erfragt das Bild für das Verlassen im POST mit request
            if not file or file.filename == "": # Falls kein Bild für das Verlassen im POST
                if SHOW_PRINTS:
                    print("\n===== KEIN BILD ERHALTEN =====\n\n======== POST ENDE ========")
                return "===== KEIN BILD ERHALTEN =====", 400
        image = convert_img(file) # image bekommt ein konvertiertes Bild von file
        if image is None: # Falls Bild ungültig
            if SHOW_PRINTS:
                print("===== ÜNGÜLTIGES BILD =====\n\n======== POST ENDE ========")
            return "===== ÜNGÜLTIGES BILD =====", 400
        image = resize_image(image) # Image kleiner skalieren für Perfomance
        height, width = image.shape[:2] #image = mask_polygon(image, polygon)
        polygon = fix_camera_offset(polygon, width, height) # Einbruchsbereich richtig skalieren und positionieren
        person_count, image = yolo_analysis(image, polygon) # Analysiert das Bild und gibt es mit der Personenanzahl raus in diese 2 Variablen
        draw_polygon(polygon, image) # Zeichnet den Einbruchsbereich
        save_img(image, person_count) # Speichert das Bild

        # Je nach Ergebnis passiert etwas
        message, status = result(person_count)
        if SHOW_PRINTS:
            print("\n\n======== POST ENDE ========")    
        return message, status

    except Exception as e:
        if SHOW_PRINTS:
            print(f"\n===== FEHLER: {e}", 500)
        return f"===== FEHLER: {e}", 500


# App starten
if __name__ == '__main__':
    if os.path.exists("config.xml"):
        load_config_from_xml("config.xml")
    else:
        print("===== Konfiguraionsdatei nicht gefunden. Es werden die Standartwerte verwendet: =====")
        print_current_config()
    start_del_loop()
    if INVERT_ALARMOUTPUT == True:
        trigger_alarm_output(False)
    elif INVERT_ALARMOUTPUT == False:
        trigger_alarm_output(False)
    else:
        print("===== Interner Fehler (trigger-start) =====")
    app.run(host=HTTP_IP, port=HTTP_PORT)


