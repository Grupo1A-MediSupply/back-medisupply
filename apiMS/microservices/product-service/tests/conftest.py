"""
Fixtures y configuración para tests de Product Service
"""
import pytest
from unittest.mock import Mock, AsyncMock
import sys
from pathlib import Path

# Agregar paths al PYTHONPATH
product_service_path = str(Path(__file__).parent.parent)
shared_path = str(Path(__file__).parent.parent.parent / "shared")
if product_service_path not in sys.path:
    sys.path.insert(0, product_service_path)
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

# Imports se harán en las fixtures cuando sea necesario
# para evitar problemas de imports circulares


@pytest.fixture
def product_id():
    """Fixture para ID de producto"""
    from shared.domain.value_objects import EntityId
    return EntityId("prod-123")


@pytest.fixture
def product_name():
    """Fixture para nombre de producto"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from domain.value_objects import ProductName
    return ProductName("Laptop Dell")


@pytest.fixture
def product_description():
    """Fixture para descripción"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from domain.value_objects import ProductDescription
    return ProductDescription("Laptop de alto rendimiento")


@pytest.fixture
def product_price():
    """Fixture para precio"""
    from shared.domain.value_objects import Money
    return Money(1299.99)


@pytest.fixture
def product_stock():
    """Fixture para stock"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from domain.value_objects import Stock
    return Stock(10)


@pytest.fixture
def product(product_id, product_name, product_price, product_description, product_stock):
    """Fixture para entidad Product"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from domain.entities import Product
    return Product(
        product_id=product_id,
        name=product_name,
        price=product_price,
        description=product_description,
        stock=product_stock,
        is_active=True
    )


@pytest.fixture
def mock_product_repository():
    """Mock del repositorio de productos"""
    repository = Mock()
    repository.save = AsyncMock()
    repository.find_by_id = AsyncMock()
    repository.find_by_name = AsyncMock()
    repository.find_all = AsyncMock()
    repository.delete = AsyncMock()
    repository.exists_by_id = AsyncMock(return_value=False)
    return repository

