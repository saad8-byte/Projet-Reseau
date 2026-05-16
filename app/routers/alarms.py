"""
app/routers/alarms.py
GET  /alarms          → last 20 unresolved alarms
POST /alarms          → create alarm (called by bridge on anomaly)
PUT  /alarms/{id}/resolve → mark resolved
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.models.db import get_conn

router = APIRouter()

MOCK_ALARMS = [
    {"id":1,"sensor_id":"IOT-01","severity":"medium",
     "message":"Temperature above 35°C threshold","resolved":0,
     "created_at":"2026-05-17T07:55:00"},
]

class AlarmCreate(BaseModel):
    sensor_id: str
    severity:  Optional[str] = "medium"
    message:   str

@router.get("/")
def list_alarms(limit: int = 20):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM alarms WHERE resolved=0 ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        result = [dict(r) for r in rows]
        return result if result else MOCK_ALARMS
    finally:
        conn.close()

@router.post("/")
def create_alarm(alarm: AlarmCreate):
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO alarms (sensor_id, severity, message) VALUES (?,?,?)",
            (alarm.sensor_id, alarm.severity, alarm.message)
        )
        conn.commit()
        return {"ok": True, "id": cur.lastrowid}
    finally:
        conn.close()

@router.put("/{alarm_id}/resolve")
def resolve_alarm(alarm_id: int):
    conn = get_conn()
    try:
        if not conn.execute("SELECT id FROM alarms WHERE id=?", (alarm_id,)).fetchone():
            raise HTTPException(404, "Alarm not found")
        conn.execute("UPDATE alarms SET resolved=1 WHERE id=?", (alarm_id,))
        conn.commit()
        return {"ok": True, "resolved": alarm_id}
    finally:
        conn.close()