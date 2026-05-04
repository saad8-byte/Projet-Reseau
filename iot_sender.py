# ─────────────────────────────────────────────
#  VM IoT Client — envoie les données capteurs
#  Usage : python iot_sender.py
# ─────────────────────────────────────────────
import requests, time, random, math

API_URL = "http://192.168.1.50:8000"   # ← remplace par l'IP de la machine API

SENSORS = [
    {"id": "IOT-01", "name": "Température Bureau",    "base": 23.0, "unit": "°C",  "noise": 0.5},
    {"id": "IOT-02", "name": "Humidité Salle Srv",    "base": 58.0, "unit": "%",   "noise": 1.0},
    {"id": "IOT-03", "name": "Pression Atm.",         "base": 1013, "unit": "hPa", "noise": 0.5},
    {"id": "IOT-04", "name": "CO2 Laboratoire",       "base": 412,  "unit": "ppm", "noise": 5.0},
    {"id": "IOT-05", "name": "Luminosité Extérieure", "base": 8340, "unit": "lux", "noise": 100},
    {"id": "IOT-06", "name": "Vibration Machine",     "base": 0.02, "unit": "g",   "noise": 0.002},
]

def send_sensor(sensor, value, status="online"):
    try:
        r = requests.post(f"{API_URL}/sensor-event", json={
            "sensor_id": sensor["id"],
            "name": sensor["name"],
            "value": round(value, 3),
            "unit": sensor["unit"],
            "status": status
        }, timeout=3)
        print(f"[✓] {sensor['id']} = {round(value,3)} {sensor['unit']}")
    except Exception as e:
        print(f"[✗] Erreur : {e}")

print("=== IoT Sensor Sender ===")
print("Envoi continu toutes les 2 secondes. Ctrl+C pour arrêter.\n")

t = 0
while True:
    for s in SENSORS:
        val = s["base"] + math.sin(t * 0.1) * s["noise"] + random.uniform(-s["noise"]*0.3, s["noise"]*0.3)
        status = "warning" if s["id"] == "IOT-04" and val > 450 else "online"
        send_sensor(s, val, status)
    t += 1
    time.sleep(2)
