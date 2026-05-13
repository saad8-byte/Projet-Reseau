# ─────────────────────────────────────────────
#  IoT VPN Shield — FastAPI Backend
#  Lance avec : uvicorn main:app --host 0.0.0.0 --port 8000
# ─────────────────────────────────────────────

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import asyncio, json, os

app = FastAPI(title="IoT VPN Shield API", version="1.0.0")

# ── CORS : autorise le dashboard à se connecter depuis n'importe quelle origine
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Sert le dashboard HTML si présent dans le dossier static/
if os.path.exists("../dashboard"):
    app.mount("/", StaticFiles(directory="../dashboard", html=True), name="static")


# ─────────────────────────────────────────────
#  MODÈLES DE DONNÉES
# ─────────────────────────────────────────────

class SensorEvent(BaseModel):
    sensor_id: str                # "IOT-01"
    name: str                     # "Température Bureau"
    ip: str                       # "192.168.1.50"
    value: float                  # 23.4
    unit: str                     # "°C"
    status: str                   # "online" | "warning" | "offline"
    vpn_active: bool              # True/False

class AttackEvent(BaseModel):
    type: str                     # "ARP", "NMAP", "DOS", "WSHARK"
    description: str              # texte libre
    target: str                   # IP cible
    blocked: bool                 # True si le VPN a bloqué l'attaque

class MetricsEvent(BaseModel):
    latency_ms: float             # 12.3
    cpu_percent: float            # 3.1
    bandwidth_mbps: float         # 94.2
    packets_per_sec: Optional[float] = 0.0


# ─────────────────────────────────────────────
#  GESTIONNAIRE DE CONNEXIONS WEBSOCKET
# ─────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)
        print(f"[WS] Client connecté — {len(self.active)} connecté(s)")

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)
        print(f"[WS] Client déconnecté — {len(self.active)} connecté(s)")

    async def broadcast(self, data: dict):
        """Envoie un message JSON à tous les clients connectés."""
        msg = json.dumps(data)
        dead = []
        for ws in self.active:
            try:
                await ws.send_text(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

manager = ConnectionManager()


# ─────────────────────────────────────────────
#  STOCKAGE EN MÉMOIRE
# ─────────────────────────────────────────────

history = {
    "sensors": {},
    "attacks": [],
    "metrics": [],
}


# ─────────────────────────────────────────────
#  WEBSOCKET — /ws
# ─────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    # Envoie l'historique au nouveau client dès sa connexion
    await websocket.send_text(json.dumps({
        "type": "history",
        "sensors": list(history["sensors"].values()),
        "attacks": history["attacks"][-20:],
        "metrics": history["metrics"][-30:],
    }))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ─────────────────────────────────────────────
#  ENDPOINTS REST
# ─────────────────────────────────────────────

@app.post("/api/sensor")
async def receive_sensor(event: SensorEvent):
    """Reçoit les données des capteurs IoT"""
    payload = {
        "type": "sensor",
        "time": datetime.now().strftime("%H:%M:%S"),
        "data": event.dict()
    }
    history["sensors"][event.sensor_id] = payload

    await manager.broadcast(payload)
    print(f"[SENSOR] {event.sensor_id} = {event.value}{event.unit} ({event.status})")
    return {"status": "ok", "broadcast_to": len(manager.active)}


@app.post("/api/attack")
async def receive_attack(event: AttackEvent):
    """Reçoit les attaques Kali Linux"""
    payload = {
        "type": "attack",
        "time": datetime.now().strftime("%H:%M:%S"),
        "data": event.dict()
    }
    history["attacks"].append(payload)
    if len(history["attacks"]) > 50:
        history["attacks"].pop(0)

    await manager.broadcast(payload)
    print(f"[ATTACK] {event.type} → {event.target} | bloqué={event.blocked}")
    return {"status": "ok", "broadcast_to": len(manager.active)}


@app.post("/api/metrics")
async def receive_metrics(event: MetricsEvent):
    """Reçoit les métriques VPN"""
    payload = {
        "type": "metrics",
        "time": datetime.now().strftime("%H:%M:%S"),
        "data": event.dict()
    }
    history["metrics"].append(payload)
    if len(history["metrics"]) > 100:
        history["metrics"].pop(0)

    await manager.broadcast(payload)
    print(f"[METRICS] Latence={event.latency_ms}ms CPU={event.cpu_percent}%")
    return {"status": "ok", "broadcast_to": len(manager.active)}


@app.get("/api/status")
async def get_status():
    """Vérifie que l'API tourne"""
    return {
        "status": "running",
        "ws_clients": len(manager.active),
        "sensors_tracked": len(history["sensors"]),
        "attacks_logged": len(history["attacks"]),
        "metrics_logged": len(history["metrics"]),
    }


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
