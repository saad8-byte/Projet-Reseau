from fastapi import APIRouter, Query
from typing import Optional
from app.models.db import get_conn
from app.config import settings

router = APIRouter()

@router.get("/")
def get_readings(limit: int = Query(10, ge=1, le=200), sensor_id: Optional[str] = None):
    conn = get_conn()
    try:
        q, p = "SELECT * FROM telemetry", []
        if sensor_id:
            q += " WHERE sensor_id = ?"; p.append(sensor_id)
        q += " ORDER BY received_at DESC LIMIT ?"; p.append(limit)
        return [dict(r) for r in conn.execute(q, p).fetchall()]
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
        return {
            "sensors_total":   total,
            "sensors_active":  active,
            "sensors_offline": total - active,
            "total_readings":  n_reads,
            "vpn_capacity":    settings.VPN_MAX_PEERS,
            "vpn_used":        active,
            "vpn_pct":         round((active / settings.VPN_MAX_PEERS) * 100) if active else 0,
            "last_reading":    last[0] if last else None,
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
