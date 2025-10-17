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
    
    # Email Configuration
    mail_username: str = Field(
        default="your-email@gmail.com",
        env="MAIL_USERNAME"
    )
    mail_password: str = Field(
        default="your-app-password",
        env="MAIL_PASSWORD"
    )
    mail_from: str = Field(
        default="your-email@gmail.com",
        env="MAIL_FROM"
    )
    mail_from_name: str = Field(
        default="MediSupply Auth",
        env="MAIL_FROM_NAME"
    )
    mail_port: int = Field(default=587, env="MAIL_PORT")
    mail_server: str = Field(default="smtp.gmail.com", env="MAIL_SERVER")
    mail_starttls: bool = Field(default=True, env="MAIL_STARTTLS")
    mail_ssl_tls: bool = Field(default=False, env="MAIL_SSL_TLS")
    mail_use_credentials: bool = Field(default=True, env="MAIL_USE_CREDENTIALS")
    
    # Verification Code
    verification_code_expire_minutes: int = Field(
        default=5,
        env="VERIFICATION_CODE_EXPIRE_MINUTES"
    )
    verification_code_length: int = Field(
        default=6,
        env="VERIFICATION_CODE_LENGTH"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


# Instancia global
_settings: AuthServiceSettings | None = None


def get_settings() -> AuthServiceSettings:
    """Obtener configuración singleton"""
    global _settings
    if _settings is None:
        _settings = AuthServiceSettings()
    return _settings

