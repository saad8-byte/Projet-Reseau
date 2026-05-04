# ─────────────────────────────────────────────
#  IoT VPN Shield — API FastAPI
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
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


# ─────────────────────────────────────────────
#  MODÈLES DE DONNÉES
# ─────────────────────────────────────────────

class AttackEvent(BaseModel):
    type: str                     # "ARP", "NMAP", "DOS", "WSHARK"
    description: str              # texte libre
    target: str                   # IP cible ex: "10.0.0.2"
    blocked: bool                 # True si le VPN a bloqué l'attaque

class SensorEvent(BaseModel):
    sensor_id: str                # "IOT-01"
    name: str                     # "Température Bureau"
    value: float                  # 23.4
    unit: str                     # "°C"
    status: str                   # "online" | "warning" | "offline"

class MetricsEvent(BaseModel):
    vpn: str                      # "wireguard" | "openvpn" | "none"
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
            self.active.remove(ws)

manager = ConnectionManager()


# ─────────────────────────────────────────────
#  STOCKAGE EN MÉMOIRE (historique session)
# ─────────────────────────────────────────────

history = {
    "attacks": [],    # 50 dernières attaques
    "sensors": {},    # état actuel de chaque capteur
    "metrics": [],    # 100 dernières métriques
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
        "attacks": history["attacks"][-20:],
        "sensors": list(history["sensors"].values()),
        "metrics": history["metrics"][-30:],
    }))
    try:
        while True:
            await websocket.receive_text()   # garde la connexion vivante
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ─────────────────────────────────────────────
#  ENDPOINTS REST
# ─────────────────────────────────────────────

@app.post("/attack-event")
async def receive_attack(event: AttackEvent):
    """
    Appelé par la VM Kali Linux à chaque attaque.
    Exemple :
        requests.post("http://192.168.x.x:8000/attack-event", json={
            "type": "ARP",
            "description": "Man-in-the-middle",
            "target": "10.0.0.2",
            "blocked": True
        })
    """
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


@app.post("/sensor-event")
async def receive_sensor(event: SensorEvent):
    """
    Appelé par la VM IoT client à chaque envoi de données capteur.
    Exemple :
        requests.post("http://192.168.x.x:8000/sensor-event", json={
            "sensor_id": "IOT-01",
            "name": "Température Bureau",
            "value": 23.4,
            "unit": "°C",
            "status": "online"
        })
    """
    payload = {
        "type": "sensor",
        "time": datetime.now().strftime("%H:%M:%S"),
        "data": event.dict()
    }
    history["sensors"][event.sensor_id] = payload

    await manager.broadcast(payload)
    print(f"[SENSOR] {event.sensor_id} = {event.value}{event.unit} ({event.status})")
    return {"status": "ok", "broadcast_to": len(manager.active)}


@app.post("/metrics-event")
async def receive_metrics(event: MetricsEvent):
    """
    Appelé par la VM Monitoring (Prometheus/Grafana) après chaque mesure.
    Exemple :
        requests.post("http://192.168.x.x:8000/metrics-event", json={
            "vpn": "wireguard",
            "latency_ms": 12.3,
            "cpu_percent": 3.1,
            "bandwidth_mbps": 94.2,
            "packets_per_sec": 1240
        })
    """
    payload = {
        "type": "metrics",
        "time": datetime.now().strftime("%H:%M:%S"),
        "data": event.dict()
    }
    history["metrics"].append(payload)
    if len(history["metrics"]) > 100:
        history["metrics"].pop(0)

    await manager.broadcast(payload)
    print(f"[METRICS] VPN={event.vpn} lat={event.latency_ms}ms cpu={event.cpu_percent}%")
    return {"status": "ok", "broadcast_to": len(manager.active)}


@app.get("/status")
async def get_status():
    """Vérifie que l'API tourne — utile pour déboguer."""
    return {
        "status": "running",
        "ws_clients": len(manager.active),
        "attacks_logged": len(history["attacks"]),
        "sensors_tracked": len(history["sensors"]),
        "metrics_logged": len(history["metrics"]),
    }


@app.get("/")
async def root():
    return {"message": "IoT VPN Shield API — voir /docs pour la documentation"}
