"""
Configuración del servicio de logística
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class LogisticsServiceSettings(BaseSettings):
    """Configuración del servicio de logística"""
    
    # Servicio
    service_name: str = "logistics-service"
    service_port: int = Field(default=8004, env="LOGISTICS_SERVICE_PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Base de datos
    database_url: str = Field(
        default="sqlite:///./logistics_service.db",
        env="LOGISTICS_DATABASE_URL"
    )
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global
_settings: LogisticsServiceSettings | None = None


def get_settings() -> LogisticsServiceSettings:
    """Obtener configuración singleton"""
    global _settings
    if _settings is None:
        _settings = LogisticsServiceSettings()
    return _settings

