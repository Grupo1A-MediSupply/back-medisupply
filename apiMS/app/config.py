"""
Configuración de la aplicación usando Pydantic Settings
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Aplicación
    app_name: str = "Auth API"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Base de datos
    database_url: str = Field(default="sqlite:///./auth_api.db", env="DATABASE_URL")
    
    # Seguridad JWT
    secret_key: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    # API
    api_v1_prefix: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
_settings: Settings | None = None


def get_settings() -> Settings:
    """Obtener la instancia de configuración (singleton)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

