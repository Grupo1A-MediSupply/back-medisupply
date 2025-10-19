"""
Configuración del servicio de productos
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class ProductServiceSettings(BaseSettings):
    """Configuración del servicio de productos"""
    
    # Servicio
    service_name: str = "product-service"
    service_port: int = Field(default=8002, env="PRODUCT_SERVICE_PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Base de datos
    database_url: str = Field(
        default="sqlite:///./product_service.db",
        env="PRODUCT_DATABASE_URL"
    )
    
    # Auth Service (para validar tokens)
    auth_service_url: str = Field(
        default="http://localhost:8001",
        env="AUTH_SERVICE_URL"
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
_settings: ProductServiceSettings | None = None


def get_settings() -> ProductServiceSettings:
    """Obtener configuración singleton"""
    global _settings
    if _settings is None:
        _settings = ProductServiceSettings()
    return _settings

