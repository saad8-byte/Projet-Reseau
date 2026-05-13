# ─────────────────────────────────────────────
#  VM IoT Client — Envoie les données capteurs
#  Usage : python iot_sender.py
# ─────────────────────────────────────────────

import requests, time, random, math, os, sys, json

# ── IP de l'API : lire depuis config.json
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    else:
        print(f"⚠ Fichier {CONFIG_FILE} non trouvé. Crée-le d'abord.")
        sys.exit(1)

config = load_config()
API_URL = config.get("API_URL", "http://192.168.1.50:8000")

# ─────────────────────────────────────────────
#  CAPTEURS — modifie cette liste selon tes capteurs réels
# ─────────────────────────────────────────────

SENSORS = [
    {"id": "IOT-01", "name": "Température Bureau",    "ip": "192.168.1.10", "base": 23.0, "unit": "°C",  "noise": 0.5},
    {"id": "IOT-02", "name": "Humidité Salle Srv",    "ip": "192.168.1.11", "base": 58.0, "unit": "%",   "noise": 1.0},
    {"id": "IOT-03", "name": "Pression Atm.",         "ip": "192.168.1.12", "base": 1013, "unit": "hPa", "noise": 0.5},
    {"id": "IOT-04", "name": "CO2 Laboratoire",       "ip": "192.168.1.13", "base": 412,  "unit": "ppm", "noise": 5.0},
    {"id": "IOT-05", "name": "Luminosité Extérieure", "ip": "192.168.1.14", "base": 8340, "unit": "lux", "noise": 100},
    {"id": "IOT-06", "name": "Vibration Machine",     "ip": "192.168.1.15", "base": 0.02, "unit": "g",   "noise": 0.002},
]

# ─────────────────────────────────────────────
#  TEST DE CONNEXION À L'API
# ─────────────────────────────────────────────

def test_connection():
    print(f"[*] Test connexion vers {API_URL}/api/status ...")
    try:
        r = requests.get(f"{API_URL}/api/status", timeout=5)
        data = r.json()
        print(f"[✓] API en ligne — {data['ws_clients']} client(s) WebSocket")
        return True
    except Exception as e:
        print(f"[✗] Erreur : {e}")
        return False

# ─────────────────────────────────────────────
#  ENVOI D'UN CAPTEUR
# ─────────────────────────────────────────────

def send_sensor(sensor, value, status="online"):
    try:
        r = requests.post(f"{API_URL}/api/sensor", json={
            "sensor_id": sensor["id"],
            "name": sensor["name"],
            "ip": sensor["ip"],
            "value": round(value, 3),
            "unit": sensor["unit"],
            "status": status,
            "vpn_active": True,  # À adapter selon votre setup
        }, timeout=3)
        if r.status_code == 200:
            print(f"[✓] {sensor['id']} = {round(value,3)} {sensor['unit']}  ({status})")
    except Exception as e:
        print(f"[✗] {sensor['id']} — {e}")

# ─────────────────────────────────────────────
#  BOUCLE PRINCIPALE
# ─────────────────────────────────────────────

print("=" * 50)
print("   IoT Sensor Sender — RSSP VPN Shield")
print("=" * 50)

if not test_connection():
    sys.exit(1)

print(f"\n[*] Envoi de {len(SENSORS)} capteurs toutes les 2s\n")

t = 0
while True:
    print(f"── Cycle {t+1} ─────────────────")
    for s in SENSORS:
        val = (s["base"]
               + math.sin(t * 0.1) * s["noise"]
               + random.uniform(-s["noise"] * 0.3, s["noise"] * 0.3))
        
        # Logique de statut
        status = "online"
        if s["id"] == "IOT-04" and val > 450:
            status = "warning"

        send_sensor(s, val, status)

    t += 1
    time.sleep(2)
