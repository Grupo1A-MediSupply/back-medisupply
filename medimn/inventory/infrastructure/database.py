"""
Configuración de base de datos (adaptado para monolito)
Usa la base de datos unificada del monolito
"""
import sys
from pathlib import Path

# Agregar path del monolito
monolith_path = Path(__file__).parent.parent.parent
if str(monolith_path) not in sys.path:
    sys.path.insert(0, str(monolith_path))

# Usar la base de datos unificada del monolito
from infrastructure.database import (
    Base,
    engine,
    SessionLocal,
    get_db as get_db_unified
)

# Re-exportar para compatibilidad
__all__ = ["Base", "engine", "SessionLocal", "get_db", "create_tables"]

def get_db():
    """Dependency para obtener sesión de base de datos"""
    return get_db_unified()

def create_tables():
    """Crear tablas (las tablas se crean desde main.py del monolito)"""
    pass
