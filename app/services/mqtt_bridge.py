import json
import logging
import sqlite3
import paho.mqtt.client as mqtt

DB_PATH = "/home/iot-client-1/Projet-Reseau/database/iot_telemetry.db"
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "iot/sensors/+/telemetry"
VALID_SENSOR_TYPES = ("temperature", "humidity", "pressure")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MQTT_SQLITE_BRIDGE")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        logger.info("Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC)
        logger.info(f"Subscribed to: {MQTT_TOPIC}")
    else:
        logger.error(f"MQTT connection failed: {reason_code}")
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        required = ["sensor_id", "sensor_type", "value", "battery", "status", "timestamp"]
        for field in required:
            if field not in payload:
                raise ValueError(f"Missing field: {field}")
        if payload["sensor_type"] not in VALID_SENSOR_TYPES:
            raise ValueError(f"Invalid sensor_type: {payload['sensor_type']}")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO telemetry
            (sensor_id, sensor_type, value, battery, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            payload["sensor_id"],
            payload["sensor_type"],
            float(payload["value"]),
            int(payload["battery"]),
            payload["status"],
payload["timestamp"]
        ))
        conn.commit()
        conn.close()
        logger.info(f"Telemetry inserted -> {payload['sensor_id']} | {payload['sensor_type']}")
    except Exception as e:
        logger.error(f"Error: {e}")

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

if __name__ == "__main__":
    logger.info("Starting MQTT SQLite Bridge...")
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Bridge stopped manually")
    except Exception as e:
        logger.error(f"Fatal error: {e}")