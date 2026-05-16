import sqlite3, os
from app.config import settings

def get_conn():
    os.makedirs(os.path.dirname(settings.DB_PATH), exist_ok=True)
    conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS sensors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_id TEXT UNIQUE NOT NULL,
        ip_address TEXT,
        sensor_type TEXT DEFAULT 'unknown',
        status TEXT DEFAULT 'active',
        registered_at TEXT DEFAULT (datetime('now')))""")
    cur.execute("""CREATE TABLE IF NOT EXISTS telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_id TEXT NOT NULL,
        timestamp TEXT,
        temperature REAL,
        humidity REAL,
        pressure REAL,
        battery INTEGER,
        unit TEXT,
        status TEXT,
        received_at TEXT DEFAULT (datetime('now')))""")
    cur.execute("""CREATE TABLE IF NOT EXISTS alarms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_id TEXT,
        severity TEXT DEFAULT 'medium',
        message TEXT,
        resolved INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')))""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tel_time ON telemetry(received_at DESC)")
    conn.commit()
    conn.close()
