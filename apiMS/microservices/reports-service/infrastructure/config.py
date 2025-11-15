"""
Configuración del servicio de reportes
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class ReportsServiceSettings(BaseSettings):
    """Configuración del servicio de reportes"""
    
    # Servicio
    service_name: str = "reports-service"
    service_port: int = Field(default=8006, env="REPORTS_SERVICE_PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
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
    order_service_url: str = Field(
        default="http://order-service:8003",
        env="ORDER_SERVICE_URL"
    )
    product_service_url: str = Field(
        default="http://product-service:8002",
        env="PRODUCT_SERVICE_URL"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global
_settings: ReportsServiceSettings | None = None


def get_settings() -> ReportsServiceSettings:
    """Obtener configuración singleton"""
    global _settings
    if _settings is None:
        _settings = ReportsServiceSettings()
    return _settings

