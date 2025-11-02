"""
Configuración del servicio de órdenes
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class OrderServiceSettings(BaseSettings):
    """Configuración del servicio de órdenes"""
    
    # Servicio
    service_name: str = "order-service"
    service_port: int = Field(default=8003, env="ORDER_SERVICE_PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Base de datos
    database_url: str = Field(
        default="sqlite:///./order_service.db",
        env="ORDER_DATABASE_URL"
    )
    
    # Servicios externos
    product_service_url: str = Field(
        default="http://product-service:8002",
        env="PRODUCT_SERVICE_URL"
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
_settings: OrderServiceSettings | None = None


def get_settings() -> OrderServiceSettings:
    """Obtener configuración singleton"""
    global _settings
    if _settings is None:
        _settings = OrderServiceSettings()
    return _settings

