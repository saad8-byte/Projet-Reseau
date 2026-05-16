"""
app/routers/vpn.py
GET /vpn/status  → active peers from `wg show`
GET /vpn/gauge   → capacity gauge data for dashboard
"""
from fastapi import APIRouter
from app.services.provisioning import get_peer_status
from app.config import settings
from app.models.db import get_conn

router = APIRouter()

@router.get("/status")
def vpn_status():
    peers = get_peer_status()
    return {
        "peers":          peers,
        "active_tunnels": len(peers),
        "server_ip":      settings.WG_SERVER_IP,
        "subnet":         settings.WG_SUBNET,
    }

@router.get("/gauge")
def vpn_gauge():
    conn = get_conn()
    try:
        active = conn.execute(
            "SELECT COUNT(*) FROM sensors WHERE status='active'"
        ).fetchone()[0]
        return {
            "used":      active,
            "max":       settings.VPN_MAX_PEERS,
            "pct":       round((active / settings.VPN_MAX_PEERS) * 100),
            "available": settings.VPN_MAX_PEERS - active,
        }
    finally:
        conn.close()