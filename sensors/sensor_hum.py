import requests
import time
import random
import subprocess
import json
import os
import sys
from datetime import datetime

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "..", "config", "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    print(f"[ERREUR] {CONFIG_FILE} introuvable")
    sys.exit(1)

config = load_config()
API_URL = config.get("API_URL", "http://10.0.0.1:8000")

SENSOR = {
    "sensor_id": "IOT2",
    "name": "Humidité Entrepôt",
    "ip": "10.0.0.11",
    "unit": "%",
    "sensor_type": "humidity"
}

session = requests.Session()

def vpn_status():
    """Vérifie si le VPN est actif via WireGuard"""
    try:
        result = subprocess.run(
            ["wg", "show"],
            capture_output=True,
            text=True,
            timeout=3
        )
        output = result.stdout.lower()
        return "latest handshake" in output or "transfer" in output
    except Exception:
        return False

print("=" * 50)
print(f"[+] {SENSOR['sensor_id']} Started")
print("=" * 50)

current_humidity = 55.0

while True:
    try:
        # Simulation réaliste
        current_humidity += random.uniform(-0.8, 0.8)
        current_humidity = max(30, min(current_humidity, 90))
        humidity = round(current_humidity, 2)

        # Seuils industriels
        if humidity > 80:
            status = "critical"
        elif humidity > 70:
            status = "warning"
        else:
            status = "online"

        payload = {
            **SENSOR,
            "value": humidity,
            "status": status,
            "vpn_active": vpn_status(),
            "timestamp": datetime.now().isoformat()
        }

        response = session.post(
            f"{API_URL}/api/sensor",
            json=payload,
            timeout=5
        )

        now = datetime.now().strftime("%H:%M:%S")
        vpn_state = "ON" if payload["vpn_active"] else "OFF"
        
        if response.status_code == 200:
            print(f"[{now}] {status.upper()} | {humidity}% | VPN: {vpn_state}")
        else:
            print(f"[{now}] API ERROR {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("[ERREUR] API inaccessible - Vérifiez le VPN")
    except KeyboardInterrupt:
        print("\n[STOP] Capteur arrêté")
        break
    except Exception as e:
        print(f"[ERREUR] {e}")

    time.sleep(5)
