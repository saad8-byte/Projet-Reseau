import paho.mqtt.client as mqtt
import json
import time
import random
import os
import ssl
import logging
from datetime import datetime, timezone

# ==========================================
# CONFIGURATION LOGS
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("SensorAgent")

# ==========================================
# CHARGEMENT .ENV
# ==========================================
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, value = line.split("=", 1)
                os.environ[key] = value
        logger.info("✅ Variables .env chargées")
    except FileNotFoundError:
        logger.warning("⚠️ Fichier .env introuvable, utilisation des valeurs par défaut")

load_env()

# ==========================================
# CONFIGURATION MQTT & CAPTEUR
# ==========================================
BROKER_URL = os.getenv("BROKER_URL", "10.0.0.1")
PORT = int(os.getenv("BROKER_PORT", "8883"))

MQTT_USER = os.getenv("MQTT_SENSOR_USER", "iotuser")
MQTT_PASS = os.getenv("MQTT_SENSOR_PASS", "admin")

SENSOR_ID = os.getenv("SENSOR_ID", "temp001")
SENSOR_TYPE = os.getenv("SENSOR_TYPE", "temperature")
UNIT = os.getenv("UNIT", "°C")
MIN_VAL = float(os.getenv("MIN_VAL", "15.0"))
MAX_VAL = float(os.getenv("MAX_VAL", "35.0"))
INTERVAL = int(os.getenv("INTERVAL_S", "2"))

USE_TLS = os.getenv("USE_TLS", "false").lower() == "true"
CA_CERT = os.getenv("CA_CERT_PATH")

TOPIC_TELEMETRY = f"iot/sensors/{SENSOR_ID}/telemetry"
TOPIC_STATUS = f"iot/sensors/{SENSOR_ID}/status"

# ==========================================
# MQTT CALLBACKS
# ==========================================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(f"✅ Connecté au broker MQTT VPN : {BROKER_URL}")
        status_payload = {
            "sensor_id": SENSOR_ID,
            "sensor_type": SENSOR_TYPE,
            "status": "online",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        client.publish(TOPIC_STATUS, json.dumps(status_payload), qos=1, retain=True)
    else:
        logger.error(f"❌ Erreur connexion MQTT : {rc}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.warning("⚠️ Déconnexion inattendue du broker")
    else:
        logger.info("🔌 Déconnecté proprement")

def on_publish(client, userdata, mid):
    logger.debug(f"✔️ Message publié (mid=[{mid}])")

# ==========================================
# GÉNÉRATION PAYLOAD
# ==========================================
def generate_payload():
    now = datetime.now(timezone.utc).isoformat()
    value = round(random.uniform(MIN_VAL, MAX_VAL), 1)
    battery = random.randint(85, 100)

    payload = {
        "sensor_id": SENSOR_ID,
        "sensor_type": SENSOR_TYPE,
        "timestamp": now,
        "value": value,
        "unit": UNIT,
        "battery": battery,
        "status": "ok"
    }
    return payload

# ==========================================
# VALIDATION PAYLOAD
# ==========================================
def validate_payload(payload):
    required_keys = {"sensor_id", "sensor_type", "timestamp", "value", "unit", "battery", "status"}
    return required_keys.issubset(payload.keys()) and payload["value"] is not None

# ==========================================
# CRÉATION CLIENT MQTT
# ==========================================
def create_mqtt_client():
    client = mqtt.Client(client_id=f"sensor_{SENSOR_ID}", clean_session=True)

    if MQTT_USER and MQTT_PASS:
        client.username_pw_set(MQTT_USER, MQTT_PASS)

    if USE_TLS:
        try:
            if CA_CERT and os.path.exists(CA_CERT):
                client.tls_set(ca_certs=CA_CERT, cert_reqs=ssl.CERT_REQUIRED)
            else:
                client.tls_set(cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLS_CLIENT)
                client.tls_insecure_set(True)
            logger.info("🔒 TLS activé")
        except Exception as e:
            logger.warning(f"⚠️ Échec configuration TLS : {e}")

    will_payload = json.dumps({
        "sensor_id": SENSOR_ID,
        "sensor_type": SENSOR_TYPE,
        "status": "offline",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    client.will_set(TOPIC_STATUS, will_payload, qos=1, retain=True)
    
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    client.reconnect_delay_set(min_delay=2, max_delay=10)

    return client

# ==========================================
# MAIN
# ==========================================
def main():
    client = create_mqtt_client()

    try:
        logger.info(f"🚀 Démarrage agent {SENSOR_ID} ({SENSOR_TYPE})")
        client.connect(BROKER_URL, PORT, keepalive=60)
        client.loop_start()

        while True:
            if client.is_connected():
                payload = generate_payload()
                
                if not validate_payload(payload):
                    logger.error("❌ Payload invalide, skip")
                    continue

                result = client.publish(TOPIC_TELEMETRY, json.dumps(payload), qos=1)
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    logger.info(f"📡 {SENSOR_TYPE.capitalize()} : {payload['value']}{payload['unit']} | Bat: {payload['battery']}%")
                else:
                    logger.warning(f"⚠️ Échec publication (RC: {result.rc})")
            else:
                logger.warning("⚠️ Broker indisponible, tentative de reconnexion...")
            
            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        logger.info("🛑 Arrêt manuel demandé")
    except Exception as e:
        logger.critical(f"💥 Erreur critique : {e}")
    finally:
        try:
            client.loop_stop()
            client.disconnect()
        except:
            pass

if __name__ == "__main__":
    main()
