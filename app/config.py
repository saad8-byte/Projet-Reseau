from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DEMO_MODE: bool = True
    DATABASE_URL: str = "sqlite:///./iot.db"
    MQTT_BROKER: str = "mqtt://localhost:1883"
    MQTT_USER: Optional[str] = None
    MQTT_PASS: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()