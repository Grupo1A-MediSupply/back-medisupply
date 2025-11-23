"""
Configuración del servicio de order (adaptado para monolito)
"""
import sys
from pathlib import Path

# Agregar path del monolito
monolith_path = Path(__file__).parent.parent.parent
if str(monolith_path) not in sys.path:
    sys.path.insert(0, str(monolith_path))

# Importar configuración unificada del monolito
from infrastructure.config import get_settings as get_monolith_settings


class OrderServiceSettings:
    """Configuración del servicio de order (wrapper sobre configuración del monolito)"""
    
    def __init__(self):
        self._monolith_settings = get_monolith_settings()
    
    @property
    def service_name(self) -> str:
        return "order-service"
    
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
_settings: OrderServiceSettings | None = None


def get_settings() -> OrderServiceSettings:
    """Obtener configuración singleton"""
    global _settings
    if _settings is None:
        _settings = OrderServiceSettings()
    return _settings
