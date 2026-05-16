"""
app/routers/sensors.py
GET  /sensors         → list all
POST /sensors/onboard → register by IP (ping check)
DELETE /sensors/{id}  → remove
"""
import subprocess, platform
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.models.db import get_conn

router = APIRouter()

class OnboardRequest(BaseModel):
    sensor_id:   str
    ip_address:  str
    sensor_type: Optional[str] = "temperature"

def ping(ip: str) -> bool:
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        r = subprocess.run(["ping", param, "1", "-W", "2", ip],
                           capture_output=True, timeout=3)
        return r.returncode == 0
    except Exception:
        return False

@router.get("/")
def list_sensors():
    conn = get_conn()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM sensors ORDER BY registered_at DESC"
        ).fetchall()]
    finally:
        conn.close()

@router.post("/onboard")
def onboard(req: OnboardRequest):
    conn = get_conn()
    try:
        if conn.execute("SELECT id FROM sensors WHERE sensor_id=?",
                        (req.sensor_id,)).fetchone():
            raise HTTPException(409, f"'{req.sensor_id}' already registered")
        reachable = ping(req.ip_address)
        conn.execute(
            "INSERT INTO sensors (sensor_id, ip_address, sensor_type, status) VALUES (?,?,?,?)",
            (req.sensor_id, req.ip_address, req.sensor_type, "active")
        )
        conn.commit()
        return {"ok": True, "sensor_id": req.sensor_id,
                "ping": "ok" if reachable else "no reply (registered anyway)"}
    finally:
        conn.close()

@router.delete("/{sensor_id}")
def delete_sensor(sensor_id: str):
    conn = get_conn()
    try:
        if not conn.execute("SELECT id FROM sensors WHERE sensor_id=?",
                            (sensor_id,)).fetchone():
            raise HTTPException(404, "Not found")
        conn.execute("DELETE FROM sensors WHERE sensor_id=?", (sensor_id,))
        conn.commit()
        return {"ok": True, "deleted": sensor_id}
    finally:
        conn.close()