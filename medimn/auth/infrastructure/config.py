"""
Configuración del servicio de autenticación (adaptado para monolito)
"""
import sys
from pathlib import Path

# Agregar path del monolito
monolith_path = Path(__file__).parent.parent.parent
if str(monolith_path) not in sys.path:
    sys.path.insert(0, str(monolith_path))

# Importar configuración unificada del monolito
from infrastructure.config import get_settings as get_monolith_settings


class AuthServiceSettings:
    """Configuración del servicio de autenticación (wrapper sobre configuración del monolito)"""
    
    def __init__(self):
        self._monolith_settings = get_monolith_settings()
    
    @property
    def service_name(self) -> str:
        return "auth-service"
    
    @property
    def service_port(self) -> int:
        return self._monolith_settings.service_port
    
    @property
    def environment(self) -> str:
        return self._monolith_settings.environment
    
    @property
    def debug(self) -> bool:
        return self._monolith_settings.debug
    
    @property
    def database_url(self) -> str:
        return self._monolith_settings.database_url
    
    @property
    def secret_key(self) -> str:
        return self._monolith_settings.secret_key
    
    @property
    def algorithm(self) -> str:
        return self._monolith_settings.algorithm
    
    @property
    def access_token_expire_minutes(self) -> int:
        return self._monolith_settings.access_token_expire_minutes
    
    @property
    def allowed_origins(self) -> list:
        return self._monolith_settings.allowed_origins
    
    @property
    def mail_username(self) -> str:
        return self._monolith_settings.mail_username
    
    @property
    def mail_password(self) -> str:
        return self._monolith_settings.mail_password
    
    @property
    def mail_from(self) -> str:
        return self._monolith_settings.mail_from
    
    @property
    def mail_from_name(self) -> str:
        return self._monolith_settings.mail_from_name
    
    @property
    def mail_port(self) -> int:
        return self._monolith_settings.mail_port
    
    @property
    def mail_server(self) -> str:
        return self._monolith_settings.mail_server
    
    @property
    def mail_starttls(self) -> bool:
        return self._monolith_settings.mail_starttls
    
    @property
    def mail_ssl_tls(self) -> bool:
        return self._monolith_settings.mail_ssl_tls
    
    @property
    def mail_use_credentials(self) -> bool:
        return self._monolith_settings.mail_use_credentials
    
    @property
    def mail_simulate(self) -> bool:
        return self._monolith_settings.mail_simulate
    
    @property
    def verification_code_expire_minutes(self) -> int:
        return self._monolith_settings.verification_code_expire_minutes
    
    @property
    def verification_code_length(self) -> int:
        return self._monolith_settings.verification_code_length


# Instancia global
_settings: AuthServiceSettings | None = None


def get_settings() -> AuthServiceSettings:
    """Obtener configuración singleton"""
    global _settings
    if _settings is None:
        _settings = AuthServiceSettings()
    return _settings
