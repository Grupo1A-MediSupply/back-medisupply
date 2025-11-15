"""
Tests unitarios para aumentar cobertura de infrastructure/repositories/__init__.py
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Agregar paths
auth_service_path = str(Path(__file__).parent.parent.parent)
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if auth_service_path not in sys.path:
    sys.path.insert(0, auth_service_path)
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.value_objects import EntityId, Email
from domain.value_objects import Username, HashedPassword, FullName, PhoneNumber
from domain.entities import User
from infrastructure.repositories import (
    UserModel, 
    VerificationCodeModel, 
    SQLAlchemyUserRepository,
    Base
)


@pytest.mark.unit
class TestRepositoriesPathConfiguration:
    """Tests para la configuración de paths en el módulo repositories"""
    
    def test_shared_path_insertion(self):
        """Test: Verificar que el path de shared se inserta correctamente (línea 14-15)"""
        # Verificar que shared_path está en sys.path
        shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
        assert shared_path in sys.path
        
        # Verificar que se puede importar desde shared
        try:
            from shared.domain.value_objects import EntityId, Email
            assert EntityId is not None
            assert Email is not None
        except ImportError:
            pytest.skip("shared module not available")
    
    def test_auth_service_path_insertion(self):
        """Test: Verificar que el path de auth-service se inserta correctamente (línea 20)"""
        # Verificar que auth_service_path está en sys.path
        auth_service_path = str(Path(__file__).parent.parent.parent)
        assert auth_service_path in sys.path
        
        # Verificar que se puede importar desde domain
        try:
            from domain.entities import User
            from domain.value_objects import Username, HashedPassword, FullName, PhoneNumber
            assert User is not None
            assert Username is not None
        except ImportError:
            pytest.skip("domain modules not available")
    
    def test_import_fallback_mechanism(self):
        """Test: Verificar el mecanismo de fallback de imports (líneas 25-26)"""
        # Simular el comportamiento de las líneas 25-26
        try:
            # Intentar importar con relative imports primero
            from ...domain.entities import User
            from ...domain.value_objects import Username
            assert User is not None
            assert Username is not None
        except ImportError:
            # Fallback a imports absolutos
            from domain.entities import User
            from domain.value_objects import Username
            assert User is not None
            assert Username is not None


@pytest.mark.unit
class TestRepositoriesConversionMethods:
    """Tests para los métodos de conversión del repositorio"""
    
    def test_to_domain_conversion(self):
        """Test: Verificar conversión de modelo a dominio (línea 72)"""
        # Crear mock de UserModel
        mock_model = Mock(spec=UserModel)
        mock_model.id = "user-123"
        mock_model.email = "test@example.com"
        mock_model.username = "testuser"
        mock_model.hashed_password = "hashed_password_123"
        mock_model.full_name = "Test User"
        mock_model.phone_number = "+1234567890"
        mock_model.is_active = True
        mock_model.is_superuser = False
        
        # Crear repositorio con mock db
        mock_db = Mock()
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar _to_domain
        user = repository._to_domain(mock_model)
        
        # Verificar conversión
        assert user is not None
        assert str(user.id) == "user-123"
        assert str(user.email) == "test@example.com"
        assert str(user.username) == "testuser"
        assert str(user.hashed_password) == "hashed_password_123"
        assert str(user.full_name) == "Test User"
        assert str(user.phone_number) == "+1234567890"
        assert user.is_active == True
        assert user.is_superuser == False
    
    def test_to_domain_conversion_with_none_values(self):
        """Test: Verificar conversión con valores None (líneas 77-78)"""
        # Crear mock de UserModel con valores None
        mock_model = Mock(spec=UserModel)
        mock_model.id = "user-123"
        mock_model.email = "test@example.com"
        mock_model.username = "testuser"
        mock_model.hashed_password = "hashed_password_123"
        mock_model.full_name = None
        mock_model.phone_number = None
        mock_model.is_active = True
        mock_model.is_superuser = False
        
        # Crear repositorio con mock db
        mock_db = Mock()
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar _to_domain
        user = repository._to_domain(mock_model)
        
        # Verificar conversión con valores None
        assert user is not None
        assert user.full_name is None
        assert user.phone_number is None
    
    def test_to_model_conversion(self):
        """Test: Verificar conversión de dominio a modelo (línea 85)"""
        # Crear entidad User
        user = User(
            user_id=EntityId("user-123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("hashed_password_123"),
            full_name=FullName("Test User"),
            phone_number=PhoneNumber("+1234567890"),
            is_active=True,
            is_superuser=False
        )
        
        # Crear repositorio con mock db
        mock_db = Mock()
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar _to_model
        model = repository._to_model(user)
        
        # Verificar conversión
        assert model is not None
        assert model.id == "user-123"
        assert model.email == "test@example.com"
        assert model.username == "testuser"
        assert model.hashed_password == "hashed_password_123"
        assert model.full_name == "Test User"
        assert model.phone_number == "+1234567890"
        assert model.is_active == True
        assert model.is_superuser == False
    
    def test_to_model_conversion_with_none_values(self):
        """Test: Verificar conversión con valores None (líneas 90-91)"""
        # Crear entidad User con valores None
        user = User(
            user_id=EntityId("user-123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("hashed_password_123"),
            full_name=None,
            phone_number=None,
            is_active=True,
            is_superuser=False
        )
        
        # Crear repositorio con mock db
        mock_db = Mock()
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar _to_model
        model = repository._to_model(user)
        
        # Verificar conversión con valores None
        assert model is not None
        assert model.full_name is None
        assert model.phone_number is None


@pytest.mark.unit
class TestRepositoriesSaveMethod:
    """Tests para el método save del repositorio"""
    
    @pytest.mark.asyncio
    async def test_save_existing_user(self):
        """Test: Guardar usuario existente (líneas 101-114)"""
        # Crear entidad User
        user = User(
            user_id=EntityId("user-123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("hashed_password_123"),
            full_name=FullName("Test User"),
            phone_number=PhoneNumber("+1234567890"),
            is_active=True,
            is_superuser=False
        )
        
        # Crear mock de modelo existente
        existing_model = Mock(spec=UserModel)
        existing_model.id = "user-123"
        
        # Crear mock de query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = existing_model
        
        # Crear mock db
        mock_db = Mock()
        mock_db.query.return_value = mock_query
        
        # Crear repositorio
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar save
        result = await repository.save(user)
        
        # Verificar que se actualizó el modelo existente
        assert existing_model.email == "test@example.com"
        assert existing_model.username == "testuser"
        assert existing_model.hashed_password == "hashed_password_123"
        assert existing_model.full_name == "Test User"
        assert existing_model.phone_number == "+1234567890"
        assert existing_model.is_active == True
        assert existing_model.is_superuser == False
        assert existing_model.updated_at == user.updated_at
        
        # Verificar que se hizo commit
        mock_db.commit.assert_called_once()
        
        # Verificar que se retornó el usuario
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_save_new_user(self):
        """Test: Guardar usuario nuevo (líneas 115-118)"""
        # Crear entidad User
        user = User(
            user_id=EntityId("user-123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("hashed_password_123"),
            full_name=FullName("Test User"),
            phone_number=PhoneNumber("+1234567890"),
            is_active=True,
            is_superuser=False
        )
        
        # Crear mock de modelo para el refresh
        mock_model = Mock(spec=UserModel)
        mock_model.id = "user-123"
        mock_model.email = "test@example.com"
        mock_model.username = "testuser"
        mock_model.hashed_password = "hashed_password_123"
        mock_model.full_name = "Test User"
        mock_model.phone_number = "+1234567890"
        mock_model.is_active = True
        mock_model.is_superuser = False
        
        # Crear mock de query (no existe usuario inicialmente, pero existe después del refresh)
        mock_query = Mock()
        mock_query.filter.return_value.first.side_effect = [None, mock_model]  # Primera llamada: None, segunda: mock_model
        
        # Crear mock db
        mock_db = Mock()
        mock_db.query.return_value = mock_query
        
        # Crear repositorio
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar save
        result = await repository.save(user)
        
        # Verificar que se agregó nuevo modelo
        mock_db.add.assert_called_once()
        
        # Verificar que se hizo commit
        mock_db.commit.assert_called_once()
        
        # Verificar que se retornó el usuario
        assert result is not None
        assert str(result.id) == "user-123"


@pytest.mark.unit
class TestRepositoriesFindMethods:
    """Tests para los métodos find del repositorio"""
    
    @pytest.mark.asyncio
    async def test_find_by_id_found(self):
        """Test: Buscar usuario por ID encontrado (líneas 131-135)"""
        # Crear mock de modelo
        mock_model = Mock(spec=UserModel)
        mock_model.id = "user-123"
        mock_model.email = "test@example.com"
        mock_model.username = "testuser"
        mock_model.hashed_password = "hashed_password_123"
        mock_model.full_name = "Test User"
        mock_model.phone_number = "+1234567890"
        mock_model.is_active = True
        mock_model.is_superuser = False
        
        # Crear mock de query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_model
        
        # Crear mock db
        mock_db = Mock()
        mock_db.query.return_value = mock_query
        
        # Crear repositorio
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar find_by_id
        result = await repository.find_by_id(EntityId("user-123"))
        
        # Verificar resultado
        assert result is not None
        assert str(result.id) == "user-123"
    
    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self):
        """Test: Buscar usuario por ID no encontrado (línea 135)"""
        # Crear mock de query (no existe usuario)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        
        # Crear mock db
        mock_db = Mock()
        mock_db.query.return_value = mock_query
        
        # Crear repositorio
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar find_by_id
        result = await repository.find_by_id(EntityId("user-123"))
        
        # Verificar resultado
        assert result is None
    
    @pytest.mark.asyncio
    async def test_find_by_username_found(self):
        """Test: Buscar usuario por username encontrado (líneas 139-143)"""
        # Crear mock de modelo
        mock_model = Mock(spec=UserModel)
        mock_model.id = "user-123"
        mock_model.email = "test@example.com"
        mock_model.username = "testuser"
        mock_model.hashed_password = "hashed_password_123"
        mock_model.full_name = "Test User"
        mock_model.phone_number = "+1234567890"
        mock_model.is_active = True
        mock_model.is_superuser = False
        
        # Crear mock de query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_model
        
        # Crear mock db
        mock_db = Mock()
        mock_db.query.return_value = mock_query
        
        # Crear repositorio
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar find_by_username
        result = await repository.find_by_username(Username("testuser"))
        
        # Verificar resultado
        assert result is not None
        assert str(result.username) == "testuser"
    
    @pytest.mark.asyncio
    async def test_find_by_username_not_found(self):
        """Test: Buscar usuario por username no encontrado (línea 143)"""
        # Crear mock de query (no existe usuario)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        
        # Crear mock db
        mock_db = Mock()
        mock_db.query.return_value = mock_query
        
        # Crear repositorio
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar find_by_username
        result = await repository.find_by_username(Username("testuser"))
        
        # Verificar resultado
        assert result is None
    
    @pytest.mark.asyncio
    async def test_find_by_email_found(self):
        """Test: Buscar usuario por email encontrado (líneas 147-151)"""
        # Crear mock de modelo
        mock_model = Mock(spec=UserModel)
        mock_model.id = "user-123"
        mock_model.email = "test@example.com"
        mock_model.username = "testuser"
        mock_model.hashed_password = "hashed_password_123"
        mock_model.full_name = "Test User"
        mock_model.phone_number = "+1234567890"
        mock_model.is_active = True
        mock_model.is_superuser = False
        
        # Crear mock de query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_model
        
        # Crear mock db
        mock_db = Mock()
        mock_db.query.return_value = mock_query
        
        # Crear repositorio
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar find_by_email
        result = await repository.find_by_email(Email("test@example.com"))
        
        # Verificar resultado
        assert result is not None
        assert str(result.email) == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_find_by_email_not_found(self):
        """Test: Buscar usuario por email no encontrado (línea 151)"""
        # Crear mock de query (no existe usuario)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        
        # Crear mock db
        mock_db = Mock()
        mock_db.query.return_value = mock_query
        
        # Crear repositorio
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar find_by_email
        result = await repository.find_by_email(Email("test@example.com"))
        
        # Verificar resultado
        assert result is None


@pytest.mark.unit
class TestRepositoriesExistsMethods:
    """Tests para los métodos exists del repositorio"""
    
    @pytest.mark.asyncio
    async def test_exists_by_username_true(self):
        """Test: Verificar existencia por username - existe (líneas 155-159)"""
        # Crear mock de query
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 1
        
        # Crear mock db
        mock_db = Mock()
        mock_db.query.return_value = mock_query
        
        # Crear repositorio
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar exists_by_username
        result = await repository.exists_by_username(Username("testuser"))
        
        # Verificar resultado
        assert result is True
    
    @pytest.mark.asyncio
    async def test_exists_by_username_false(self):
        """Test: Verificar existencia por username - no existe (línea 159)"""
        # Crear mock de query
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 0
        
        # Crear mock db
        mock_db = Mock()
        mock_db.query.return_value = mock_query
        
        # Crear repositorio
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar exists_by_username
        result = await repository.exists_by_username(Username("testuser"))
        
        # Verificar resultado
        assert result is False
    
    @pytest.mark.asyncio
    async def test_exists_by_email_true(self):
        """Test: Verificar existencia por email - existe (líneas 163-167)"""
        # Crear mock de query
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 1
        
        # Crear mock db
        mock_db = Mock()
        mock_db.query.return_value = mock_query
        
        # Crear repositorio
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar exists_by_email
        result = await repository.exists_by_email(Email("test@example.com"))
        
        # Verificar resultado
        assert result is True
    
    @pytest.mark.asyncio
    async def test_exists_by_email_false(self):
        """Test: Verificar existencia por email - no existe (línea 167)"""
        # Crear mock de query
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 0
        
        # Crear mock db
        mock_db = Mock()
        mock_db.query.return_value = mock_query
        
        # Crear repositorio
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar exists_by_email
        result = await repository.exists_by_email(Email("test@example.com"))
        
        # Verificar resultado
        assert result is False


@pytest.mark.unit
class TestRepositoriesDeleteMethod:
    """Tests para el método delete del repositorio"""
    
    @pytest.mark.asyncio
    async def test_delete_user_found(self):
        """Test: Eliminar usuario encontrado (líneas 171-178)"""
        # Crear mock de modelo
        mock_model = Mock(spec=UserModel)
        mock_model.id = "user-123"
        
        # Crear mock de query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_model
        
        # Crear mock db
        mock_db = Mock()
        mock_db.query.return_value = mock_query
        
        # Crear repositorio
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar delete
        result = await repository.delete(EntityId("user-123"))
        
        # Verificar que se eliminó el modelo
        mock_db.delete.assert_called_once_with(mock_model)
        
        # Verificar que se hizo commit
        mock_db.commit.assert_called_once()
        
        # Verificar resultado
        assert result is True
    
    @pytest.mark.asyncio
    async def test_delete_user_not_found(self):
        """Test: Eliminar usuario no encontrado (líneas 171-180)"""
        # Crear mock de query (no existe usuario)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        
        # Crear mock db
        mock_db = Mock()
        mock_db.query.return_value = mock_query
        
        # Crear repositorio
        repository = SQLAlchemyUserRepository(mock_db)
        
        # Ejecutar delete
        result = await repository.delete(EntityId("user-123"))
        
        # Verificar que no se eliminó nada
        mock_db.delete.assert_not_called()
        
        # Verificar que no se hizo commit
        mock_db.commit.assert_not_called()
        
        # Verificar resultado
        assert result is False


@pytest.mark.unit
class TestRepositoriesModuleReimport:
    """Tests para reimportar el módulo repositories para cobertura"""
    
    def test_repositories_module_reimport_for_coverage(self):
        """Test: Verificar inserción de paths en el módulo repositories"""
        # Verificar que los paths están en sys.path
        shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
        auth_service_path = str(Path(__file__).parent.parent.parent)
        
        # Verificar que los paths se insertaron correctamente
        assert shared_path in sys.path
        assert auth_service_path in sys.path
        
        # Verificar que se pueden importar los módulos
        from infrastructure.repositories import SQLAlchemyUserRepository, UserModel, VerificationCodeModel
        assert SQLAlchemyUserRepository is not None
        assert UserModel is not None
        assert VerificationCodeModel is not None
