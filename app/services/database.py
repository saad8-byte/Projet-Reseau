import os
import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration centralisée
DB_DIR = os.environ.get("DB_DIR", "/home/iot-client-1/Projet-Reseau/database")
DB_PATH = os.path.join(DB_DIR, "iot_telemetry.db")

def init_db():
    """Initialise la base SQLite et active le mode WAL pour les écritures concurrentes."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA busy_timeout=5000;")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id TEXT UNIQUE NOT NULL,
            ip_address TEXT NOT NULL,
            sensor_type TEXT CHECK(sensor_type IN ('temperature', 'humidity', 'pressure')),
            status TEXT DEFAULT 'active',
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            temperature REAL,
            humidity REAL,
            pressure REAL,
            battery INTEGER,
            status TEXT,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sensor_id) REFERENCES sensors(sensor_id)
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_ts ON telemetry(received_at DESC);")
    
    conn.commit()
    conn.close()
    logger.info(f"✅ [DB] Base initialisée : {DB_PATH}")

@contextmanager
def get_db():
    """Context manager pour des connexions sûres et éphémères."""
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    try:
        yield conn
    finally:
        conn.close()

def register_sensor(sensor_id: str, ip_address: str, sensor_type: str) -> bool:
    """Enregistre un capteur. Retourne True si succès, lève IntegrityError si doublon."""
    with get_db() as conn:
        conn.execute("""
            INSERT INTO sensors (sensor_id, ip_address, sensor_type, status)
            VALUES (?, ?, ?, 'active')
        """, (sensor_id, ip_address, sensor_type))
        conn.commit()
    return True

def save_telemetry(payload: dict):
    """Insère une donnée télémétrique depuis le payload MQTT."""
    s_type = payload.get("sensor_type", "unknown")
    value = payload.get("value")
    temp = value if s_type == "temperature" else None
    hum = value if s_type == "humidity" else None
    pres = value if s_type == "pressure" else None

    with get_db() as conn:
        conn.execute("""
            INSERT INTO telemetry (sensor_id, timestamp, temperature, humidity, pressure, battery, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            payload.get("sensor_id"),
            payload.get("timestamp", datetime.now().isoformat()),
            temp, hum, pres,
            payload.get("battery"),
            payload.get("status", "ok")
        ))
        conn.commit()
    logger.info(f"💾 Télémétrie sauvegardée pour {payload.get('sensor_id')}")

def get_status():
    """Retourne l'état complet du système pour le dashboard."""
    with get_db() as conn:
        active = conn.execute("SELECT COUNT(*) FROM sensors WHERE status='active'").fetchone()[0]
        
        sensors = [dict(row) for row in conn.execute(
            "SELECT id, sensor_id, ip_address, sensor_type, status, registered_at FROM sensors ORDER BY registered_at DESC"
        ).fetchall()]
        
        telemetry = [dict(row) for row in conn.execute(
            "SELECT sensor_id, timestamp, temperature, humidity, pressure, battery, status, received_at FROM telemetry ORDER BY received_at DESC LIMIT 50"
        ).fetchall()]
        
    return {
        "capacity_max": 10,
        "capacity_used": active,
        "sensors": sensors,
        "telemetry": telemetry
    }