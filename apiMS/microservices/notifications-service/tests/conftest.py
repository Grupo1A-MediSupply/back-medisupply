"""
Fixtures y configuración para tests de Notifications Service
"""
import pytest
import sys
from pathlib import Path

# Agregar paths al PYTHONPATH antes de cualquier import
notifications_service_path = str(Path(__file__).parent.parent.resolve())
shared_path = str(Path(__file__).parent.parent.parent.resolve() / "shared")

# Configurar paths de forma más robusta
if notifications_service_path not in sys.path:
    sys.path.insert(0, notifications_service_path)
if shared_path not in sys.path:
    sys.path.insert(0, str(shared_path))

# Hook para configurar antes de que pytest recopile los tests
def pytest_configure(config):
    """Configurar paths antes de recopilar tests"""
    if notifications_service_path not in sys.path:
        sys.path.insert(0, notifications_service_path)
    if shared_path not in sys.path:
        sys.path.insert(0, str(shared_path))

