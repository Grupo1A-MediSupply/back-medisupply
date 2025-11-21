"""
Configuración del servicio de logistics (adaptado para monolito)
"""
import sys
from pathlib import Path

# Agregar path del monolito
monolith_path = Path(__file__).parent.parent.parent
if str(monolith_path) not in sys.path:
    sys.path.insert(0, str(monolith_path))

# Importar configuración unificada del monolito
from infrastructure.config import get_settings as get_monolith_settings


class LogisticsServiceSettings:
    """Configuración del servicio de logistics (wrapper sobre configuración del monolito)"""
    
    def __init__(self):
        self._monolith_settings = get_monolith_settings()
    
    @property
    def service_name(self) -> str:
        return "logistics-service"
    
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
    def allowed_origins(self) -> list:
        return self._monolith_settings.allowed_origins
    
    @property
    def auth_service_url(self) -> str:
        # En el monolito, todos los servicios están en la misma app
        return "http://localhost:8000"


# Instancia global
_settings: LogisticsServiceSettings | None = None


def get_settings() -> LogisticsServiceSettings:
    """Obtener configuración singleton"""
    global _settings
    if _settings is None:
        _settings = LogisticsServiceSettings()
    return _settings
