"""
Fixtures compartidas para tests
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta

# Agregar el path del monolito
monolith_path = Path(__file__).parent.parent
if str(monolith_path) not in sys.path:
    sys.path.insert(0, str(monolith_path))

from infrastructure.database import Base, get_db
from infrastructure.config import get_settings


@pytest.fixture(scope="function")
def db_session():
    """Fixture para crear una sesión de base de datos en memoria para tests"""
    # Crear base de datos en memoria
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Crear tablas
    Base.metadata.create_all(engine)
    
    # Crear sesión
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def mock_user_repository():
    """Mock del repositorio de usuarios"""
    repo = Mock()
    repo.find_by_id = AsyncMock(return_value=None)
    repo.find_by_username = AsyncMock(return_value=None)
    repo.find_by_email = AsyncMock(return_value=None)
    repo.exists_by_username = AsyncMock(return_value=False)
    repo.exists_by_email = AsyncMock(return_value=False)
    repo.save = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_password_hasher():
    """Mock del password hasher"""
    hasher = Mock()
    hasher.hash_password = Mock(return_value="$2b$12$hashedpassword")
    hasher.verify_password = Mock(return_value=True)
    return hasher


@pytest.fixture
def mock_token_service():
    """Mock del token service"""
    service = Mock()
    service.create_access_token = Mock(return_value="mock_access_token")
    service.create_refresh_token = Mock(return_value="mock_refresh_token")
    service.verify_access_token = Mock(return_value={"user_id": "test_user_id", "sub": "testuser"})
    service.verify_refresh_token = Mock(return_value={"user_id": "test_user_id", "sub": "testuser"})
    return service


@pytest.fixture
def mock_verification_code_repository():
    """Mock del repositorio de códigos de verificación"""
    repo = Mock()
    repo.create_verification_code = AsyncMock(return_value=Mock(
        id="code_id",
        user_id="user_id",
        code="123456",
        email="test@example.com",
        expires_at=datetime.utcnow() + timedelta(minutes=5),
        is_used=False
    ))
    repo.find_by_user_id = AsyncMock(return_value=None)
    repo.mark_as_used = AsyncMock()
    repo.db = Mock()
    repo.db.commit = Mock()
    return repo


@pytest.fixture
def sample_user_data():
    """Datos de ejemplo para un usuario"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "confirm_password": "testpass123",
        "full_name": "Test User",
        "phone_number": "+1234567890",
        "role": "client",
        "address": "123 Test St",
        "institution_name": "Test Institution"
    }


@pytest.fixture
def sample_user_entity():
    """Fixture para crear una entidad User de ejemplo"""
    from shared.domain.value_objects import EntityId, Email
    from auth.domain.value_objects import Username, HashedPassword, FullName, PhoneNumber, UserRole, Address, InstitutionName
    from auth.domain.entities import User
    
    user_id = EntityId("test-user-id-123")
    email = Email("test@example.com")
    username = Username("testuser")
    hashed_password = HashedPassword("$2b$12$hashedpassword")
    
    user = User.register(
        user_id=user_id,
        email=email,
        username=username,
        hashed_password=hashed_password,
        full_name=FullName("Test User"),
        phone_number=PhoneNumber("+1234567890"),
        role=UserRole("client"),
        address=Address("123 Test St"),
        institution_name=InstitutionName("Test Institution"),
        is_active=True,
        is_superuser=False
    )
    
    return user


@pytest.fixture
def settings():
    """Fixture para configuración de tests"""
    return get_settings()

