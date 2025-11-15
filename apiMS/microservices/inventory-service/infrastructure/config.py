"""
Configuración del servicio de inventario
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class InventoryServiceSettings(BaseSettings):
    """Configuración del servicio de inventario"""
    
    # Servicio
    service_name: str = "inventory-service"
    service_port: int = Field(default=8005, env="INVENTORY_SERVICE_PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Base de datos
    database_url: str = Field(
        default="sqlite:///./inventory_service.db",
        env="INVENTORY_DATABASE_URL"
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
_settings: InventoryServiceSettings | None = None


def get_settings() -> InventoryServiceSettings:
    """Obtener configuración singleton"""
    global _settings
    if _settings is None:
        _settings = InventoryServiceSettings()
    return _settings

