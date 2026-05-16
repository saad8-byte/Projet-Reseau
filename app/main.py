import sys
import os
import subprocess
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Ajout du dossier racine au PYTHONPATH pour les imports relatifs
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.database import init_db, register_sensor, get_status

app = FastAPI(title="IoT VPN Monitor | ENSA RSSP 2026")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

class RegisterRequest(BaseModel):
    sensor_id: str
    ip_address: str
    sensor_type: str = "temperature"

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def api_status():
    try:
        return get_status()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/register")
async def register_sensor_endpoint(req: RegisterRequest):
    if req.sensor_type not in ["temperature", "humidity", "pressure"]:
        raise HTTPException(status_code=400, detail="Type de capteur invalide")

    # Test ping
    cmd = ["ping", "-c", "1", "-W", "2", req.ip_address]
    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        if res.returncode != 0:
            raise HTTPException(status_code=400, detail="❌ Capteur injoignable (Ping échoué)")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="⏱️ Timeout ping")
    except FileNotFoundError:
        # Fallback Windows
        res = subprocess.run(["ping", "-n", "1", "-w", "2", req.ip_address], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode != 0:
            raise HTTPException(status_code=400, detail="❌ Capteur injoignable")

    try:
        register_sensor(req.sensor_id, req.ip_address, req.sensor_type)
        return {"message": f"✅ Capteur {req.sensor_id} enregistré et vérifié"}
    except Exception as e:
        if "UNIQUE" in str(e) or "duplicate" in str(e):
            raise HTTPException(status_code=409, detail="⚠️ Capteur déjà enregistré")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    init_db()  # Crée la DB au démarrage
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")