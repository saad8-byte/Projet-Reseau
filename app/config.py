from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DEMO_MODE:      bool = True
    DB_PATH:        str  = "database/iot_telemetry.db"
    MQTT_HOST:      str  = "localhost"
    MQTT_PORT:      int  = 1883
    WG_SUBNET:      str  = "10.0.0.0/24"
    WG_SERVER_IP:   str  = "10.0.0.1"
    VM1_LOCAL_IP:   str  = "192.168.0.65"
    VPN_MAX_PEERS:  int  = 10
    MASTER_API_KEY: str  = "dev-secret-2026"
    OPENAI_API_KEY: str  = ""
    OPENAI_MODEL:   str  = "gpt-3.5-turbo"

    class Config:
        env_file = ".env"
        extra    = "ignore"

settings = Settings()