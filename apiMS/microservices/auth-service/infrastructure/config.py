"""
Configuración del servicio de autenticación
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class AuthServiceSettings(BaseSettings):
    """Configuración del servicio de autenticación"""
    
    # Servicio
    service_name: str = "auth-service"
    service_port: int = Field(default=8001, env="AUTH_SERVICE_PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Base de datos
    database_url: str = Field(
        default="sqlite:///./auth_service.db",
        env="AUTH_DATABASE_URL"
    )
    
    # JWT
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
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
_settings: AuthServiceSettings | None = None


def get_settings() -> AuthServiceSettings:
    """Obtener configuración singleton"""
    global _settings
    if _settings is None:
        _settings = AuthServiceSettings()
    return _settings

