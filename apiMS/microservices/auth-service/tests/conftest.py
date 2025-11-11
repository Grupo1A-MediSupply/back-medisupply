"""
Fixtures y configuración para tests de Auth Service
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock
import sys
from pathlib import Path

# Agregar paths al PYTHONPATH
auth_service_path = str(Path(__file__).parent.parent)
shared_path = str(Path(__file__).parent.parent.parent / "shared")
if auth_service_path not in sys.path:
    sys.path.insert(0, auth_service_path)
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

# Imports se harán en las fixtures cuando sea necesario
# para evitar problemas de imports circulares


@pytest.fixture
def user_id():
    """Fixture para ID de usuario"""
    from shared.domain.value_objects import EntityId
    return EntityId("123e4567-e89b-12d3-a456-426614174000")


@pytest.fixture
def email():
    """Fixture para email"""
    from shared.domain.value_objects import Email
    return Email("test@example.com")


@pytest.fixture
def username():
    """Fixture para username"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from domain.value_objects import Username
    return Username("testuser")


@pytest.fixture
def hashed_password():
    """Fixture para contraseña hasheada"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from domain.value_objects import HashedPassword
    return HashedPassword("$2b$12$KIXxkXvHVvH3HQvK5l3Jae")


@pytest.fixture
def full_name():
    """Fixture para nombre completo"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from domain.value_objects import FullName
    return FullName("Test User")


@pytest.fixture
def user(user_id, email, username, hashed_password, full_name):
    """Fixture para entidad User"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from domain.entities import User
    return User(
        user_id=user_id,
        email=email,
        username=username,
        hashed_password=hashed_password,
        full_name=full_name,
        is_active=True,
        is_superuser=False
    )


@pytest.fixture
def mock_user_repository():
    """Mock del repositorio de usuarios"""
    repository = Mock()
    repository.save = AsyncMock()
    repository.find_by_id = AsyncMock()
    repository.find_by_username = AsyncMock()
    repository.find_by_email = AsyncMock()
    repository.exists_by_username = AsyncMock(return_value=False)
    repository.exists_by_email = AsyncMock(return_value=False)
    repository.delete = AsyncMock()
    return repository


@pytest.fixture
def mock_password_hasher():
    """Mock del hasher de contraseñas"""
    hasher = Mock()
    hasher.hash_password = Mock(return_value="$2b$12$hashed_password")
    hasher.verify_password = Mock(return_value=True)
    return hasher


@pytest.fixture
def mock_token_service():
    """Mock del servicio de tokens"""
    service = Mock()
    service.create_access_token = Mock(return_value="access_token_123")
    service.create_refresh_token = Mock(return_value="refresh_token_123")
    service.verify_access_token = Mock(return_value={
        "sub": "testuser",
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "scopes": ["read", "write"]
    })
    service.verify_refresh_token = Mock(return_value={
        "sub": "testuser",
        "user_id": "123e4567-e89b-12d3-a456-426614174000"
    })
    return service


@pytest.fixture
def mock_event_bus():
    """Mock del event bus"""
    from unittest.mock import patch
    with patch('shared.domain.events.event_bus') as mock_bus:
        mock_bus.publish = AsyncMock()
        yield mock_bus


@pytest.fixture
def mock_verification_code_repository():
    """Mock del repositorio de códigos de verificación"""
    repository = Mock()
    repository.get_valid_code = AsyncMock()
    repository.mark_code_as_used = AsyncMock()
    repository.create_verification_code = AsyncMock()
    repository.db = Mock()
    repository.db.commit = Mock()
    return repository


@pytest.fixture
def mock_email_service():
    """Mock del servicio de email"""
    service = Mock()
    service.generate_verification_code = Mock(return_value="123456")
    service.send_verification_code = AsyncMock(return_value=True)
    return service
