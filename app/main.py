"""
Colleague A owns this file.

Serves:
  - Static dashboard at GET /  (dashboard/index.html)
  - Health check at /health
  - Starts MQTT bridge on startup
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import logging

from app.config import settings
from app.models.db import init_db
from app.routers import readings, sensors, alarms, vpn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [APP] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)

# ── Path to dashboard static files ─────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASHBOARD_DIR  = os.path.join(BASE_DIR, "dashboard")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: init DB + start MQTT bridge. Shutdown: clean up."""
    # 1. Create SQLite tables if they don't exist
    log.info("Initialising database...")
    init_db()
    log.info(f"Database ready: {settings.DB_PATH}")

    # 2. Start MQTT bridge (background thread, non-blocking)
    log.info("Starting MQTT bridge...")
    from mqtt_bridge import start_bridge, register_broadcast
    start_bridge()
    log.info(f"MQTT bridge listening on {settings.MQTT_HOST}:{settings.MQTT_PORT}")

    yield  # app runs

    log.info("Shutting down.")


app = FastAPI(
    title="IoT VPN Gateway",
    version="1.0",
    lifespan=lifespan,
)

# ── API routers ─────────────────────────────────────────────────────────────
app.include_router(readings.router,   prefix="/readings",  tags=["readings"])
app.include_router(sensors.router,    prefix="/sensors",   tags=["sensors"])
app.include_router(alarms.router,     prefix="/alarms",    tags=["alarms"])
app.include_router(vpn.router,        prefix="/vpn",       tags=["vpn"])

# ── Health check ────────────────────────────────────────────────────────────
@app.get("/health", tags=["system"])
def health():
    return {
        "status":    "healthy",
        "demo_mode": settings.DEMO_MODE,
        "db":        settings.DB_PATH,
        "mqtt":      f"{settings.MQTT_HOST}:{settings.MQTT_PORT}",
    }

# ── Serve dashboard static files ────────────────────────────────────────────
# Mount JS and CSS as static
app.mount("/js",  StaticFiles(directory=os.path.join(DASHBOARD_DIR, "js")),  name="js")
app.mount("/css", StaticFiles(directory=os.path.join(DASHBOARD_DIR, "css")), name="css")

# Serve index.html at root /
@app.get("/", include_in_schema=False)
def serve_dashboard():
    return FileResponse(os.path.join(DASHBOARD_DIR, "index.html"))
