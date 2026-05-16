"""
app/routers/readings.py
GET /readings        → last 10 rows  (dashboard polls this every 3s)
GET /readings/stats  → sidebar counters + VPN gauge
GET /readings/{id}   → one sensor history
"""
from fastapi import APIRouter, Query
from typing import Optional
from app.models.db import get_conn
from app.config import settings

router = APIRouter()

MOCK = [
    {"id":1,"sensor_id":"IOT-01","temperature":23.4,"humidity":None,"pressure":None,
     "battery":87,"unit":"°C","status":"ok","received_at":"2026-05-17T08:00:00"},
    {"id":2,"sensor_id":"IOT-02","temperature":None,"humidity":61.2,"pressure":None,
     "battery":72,"unit":"%","status":"ok","received_at":"2026-05-17T08:00:02"},
]

@router.get("/")
def get_readings(limit: int = Query(10, ge=1, le=200), sensor_id: Optional[str] = None):
    conn = get_conn()
    try:
        q, p = "SELECT * FROM telemetry", []
        if sensor_id:
            q += " WHERE sensor_id = ?"; p.append(sensor_id)
        q += " ORDER BY received_at DESC LIMIT ?"; p.append(limit)
        rows = [dict(r) for r in conn.execute(q, p).fetchall()]
        return rows if rows else (MOCK[:limit] if settings.DEMO_MODE else [])
    finally:
        conn.close()

@router.get("/stats")
def get_stats():
    conn = get_conn()
    try:
        total   = conn.execute("SELECT COUNT(*) FROM sensors").fetchone()[0]
        active  = conn.execute("SELECT COUNT(*) FROM sensors WHERE status='active'").fetchone()[0]
        n_reads = conn.execute("SELECT COUNT(*) FROM telemetry").fetchone()[0]
        last    = conn.execute("SELECT received_at FROM telemetry ORDER BY received_at DESC LIMIT 1").fetchone()
        used    = active if total else 2
        return {
            "sensors_total":  total  or 2,
            "sensors_active": active or 2,
            "sensors_offline": (total - active) if total else 0,
            "total_readings": n_reads,
            "vpn_capacity":   settings.VPN_MAX_PEERS,
            "vpn_used":       used,
            "vpn_pct":        round((used / settings.VPN_MAX_PEERS) * 100),
            "last_reading":   last[0] if last else None,
        }
    finally:
        conn.close()

@router.get("/{sensor_id}")
def get_sensor_readings(sensor_id: str, limit: int = Query(50, ge=1, le=500)):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM telemetry WHERE sensor_id=? ORDER BY received_at DESC LIMIT ?",
            (sensor_id, limit)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()