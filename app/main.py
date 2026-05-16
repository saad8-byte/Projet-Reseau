from fastapi import FastAPI
from app.config import settings

app = FastAPI(title="IoT VPN Gateway", version="1.0")

@app.get("/health")
def health():
    return {"status": "healthy", "demo_mode": settings.DEMO_MODE}