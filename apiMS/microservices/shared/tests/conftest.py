"""
Fixtures y configuración para tests de Shared
"""
import sys
from pathlib import Path

# Agregar path de shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.resolve())
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

# Hook para configurar antes de que pytest recopile los tests
def pytest_configure(config):
    """Configurar paths antes de recopilar tests"""
    if shared_path not in sys.path:
        sys.path.insert(0, shared_path)

