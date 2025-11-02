"""
Configuración del servicio de notificaciones
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class NotificationsServiceSettings(BaseSettings):
    """Configuración del servicio de notificaciones"""
    
    # Servicio
    service_name: str = "notifications-service"
    service_port: int = Field(default=8007, env="NOTIFICATIONS_SERVICE_PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Base de datos
    database_url: str = Field(
        default="sqlite:///./notifications_service.db",
        env="NOTIFICATIONS_DATABASE_URL"
    )
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    # Servicios externos
    auth_service_url: str = Field(
        default="http://auth-service:8001",
        env="AUTH_SERVICE_URL"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global
_settings: NotificationsServiceSettings | None = None


def get_settings() -> NotificationsServiceSettings:
    """Obtener configuración singleton"""
    global _settings
    if _settings is None:
        _settings = NotificationsServiceSettings()
    return _settings

