"""
Tests unitarios para Query Handlers del Auth Service
"""
import pytest
from unittest.mock import Mock, AsyncMock
import sys
from pathlib import Path

# Agregar paths
auth_service_path = str(Path(__file__).parent.parent.parent)
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if auth_service_path not in sys.path:
    sys.path.insert(0, auth_service_path)
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.value_objects import EntityId, Email
from domain.value_objects import Username
from domain.entities import User
from application.queries import (
    GetUserByIdQuery, GetUserByUsernameQuery, GetUserByEmailQuery,
    VerifyTokenQuery, GetCurrentUserQuery
)
from application.handlers import (
    GetUserByIdQueryHandler, GetUserByUsernameQueryHandler,
    GetUserByEmailQueryHandler, VerifyTokenQueryHandler,
    GetCurrentUserQueryHandler
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestGetUserByIdQueryHandler:
    """Tests para GetUserByIdQueryHandler"""
    
    async def test_handle_obtiene_usuario_por_id(
        self,
        user,
        mock_user_repository
    ):
        """Test: Obtener usuario por ID exitosamente"""
        # Arrange
        mock_user_repository.find_by_id.return_value = user
        
        handler = GetUserByIdQueryHandler(mock_user_repository)
        
        query = GetUserByIdQuery(user_id="123")
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result == user
        mock_user_repository.find_by_id.assert_called_once_with(EntityId("123"))
    
    async def test_handle_usuario_no_existe(
        self,
        mock_user_repository
    ):
        """Test: Usuario no existe por ID"""
        # Arrange
        mock_user_repository.find_by_id.return_value = None
        
        handler = GetUserByIdQueryHandler(mock_user_repository)
        
        query = GetUserByIdQuery(user_id="nonexistent")
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result is None
        mock_user_repository.find_by_id.assert_called_once_with(EntityId("nonexistent"))


@pytest.mark.unit
@pytest.mark.asyncio
class TestGetUserByUsernameQueryHandler:
    """Tests para GetUserByUsernameQueryHandler"""
    
    async def test_handle_obtiene_usuario_por_username(
        self,
        user,
        mock_user_repository
    ):
        """Test: Obtener usuario por username exitosamente"""
        # Arrange
        mock_user_repository.find_by_username.return_value = user
        
        handler = GetUserByUsernameQueryHandler(mock_user_repository)
        
        query = GetUserByUsernameQuery(username="testuser")
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result == user
        mock_user_repository.find_by_username.assert_called_once_with(Username("testuser"))
    
    async def test_handle_usuario_no_existe_por_username(
        self,
        mock_user_repository
    ):
        """Test: Usuario no existe por username"""
        # Arrange
        mock_user_repository.find_by_username.return_value = None
        
        handler = GetUserByUsernameQueryHandler(mock_user_repository)
        
        query = GetUserByUsernameQuery(username="nonexistent")
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result is None
        mock_user_repository.find_by_username.assert_called_once_with(Username("nonexistent"))


@pytest.mark.unit
@pytest.mark.asyncio
class TestGetUserByEmailQueryHandler:
    """Tests para GetUserByEmailQueryHandler"""
    
    async def test_handle_obtiene_usuario_por_email(
        self,
        user,
        mock_user_repository
    ):
        """Test: Obtener usuario por email exitosamente"""
        # Arrange
        mock_user_repository.find_by_email.return_value = user
        
        handler = GetUserByEmailQueryHandler(mock_user_repository)
        
        query = GetUserByEmailQuery(email="test@example.com")
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result == user
        mock_user_repository.find_by_email.assert_called_once_with(Email("test@example.com"))
    
    async def test_handle_usuario_no_existe_por_email(
        self,
        mock_user_repository
    ):
        """Test: Usuario no existe por email"""
        # Arrange
        mock_user_repository.find_by_email.return_value = None
        
        handler = GetUserByEmailQueryHandler(mock_user_repository)
        
        query = GetUserByEmailQuery(email="nonexistent@example.com")
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result is None
        mock_user_repository.find_by_email.assert_called_once_with(Email("nonexistent@example.com"))


@pytest.mark.unit
@pytest.mark.asyncio
class TestVerifyTokenQueryHandler:
    """Tests para VerifyTokenQueryHandler"""
    
    async def test_handle_verifica_token_valido(
        self,
        mock_token_service
    ):
        """Test: Verificar token válido"""
        # Arrange
        expected_payload = {
            "sub": "testuser",
            "user_id": "123",
            "scopes": ["read", "write"]
        }
        mock_token_service.verify_access_token.return_value = expected_payload
        
        handler = VerifyTokenQueryHandler(mock_token_service)
        
        query = VerifyTokenQuery(token="valid_token")
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result["valid"] is True
        assert result["payload"] == expected_payload
        mock_token_service.verify_access_token.assert_called_once_with("valid_token")
    
    async def test_handle_verifica_token_invalido(
        self,
        mock_token_service
    ):
        """Test: Verificar token inválido"""
        # Arrange
        mock_token_service.verify_access_token.side_effect = ValueError("Token expirado")
        
        handler = VerifyTokenQueryHandler(mock_token_service)
        
        query = VerifyTokenQuery(token="invalid_token")
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result["valid"] is False
        assert "error" in result
        assert "Token expirado" in result["error"]
        mock_token_service.verify_access_token.assert_called_once_with("invalid_token")


@pytest.mark.unit
@pytest.mark.asyncio
class TestGetCurrentUserQueryHandler:
    """Tests para GetCurrentUserQueryHandler"""
    
    async def test_handle_obtiene_usuario_actual(
        self,
        user,
        mock_user_repository,
        mock_token_service
    ):
        """Test: Obtener usuario actual desde token"""
        # Arrange
        expected_payload = {
            "sub": "testuser",
            "user_id": "123",
            "scopes": ["read", "write"]
        }
        mock_token_service.verify_access_token.return_value = expected_payload
        mock_user_repository.find_by_id.return_value = user
        
        handler = GetCurrentUserQueryHandler(
            mock_user_repository,
            mock_token_service
        )
        
        query = GetCurrentUserQuery(token="valid_token")
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result == user
        mock_token_service.verify_access_token.assert_called_once_with("valid_token")
        mock_user_repository.find_by_id.assert_called_once_with(EntityId("123"))
    
    async def test_handle_token_invalido(
        self,
        mock_user_repository,
        mock_token_service
    ):
        """Test: Token inválido lanza excepción"""
        # Arrange
        mock_token_service.verify_access_token.side_effect = ValueError("Token inválido")
        
        handler = GetCurrentUserQueryHandler(
            mock_user_repository,
            mock_token_service
        )
        
        query = GetCurrentUserQuery(token="invalid_token")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Token inválido"):
            await handler.handle(query)
    
    async def test_handle_token_sin_user_id(
        self,
        mock_user_repository,
        mock_token_service
    ):
        """Test: Token sin user_id lanza excepción"""
        # Arrange
        mock_token_service.verify_access_token.return_value = {
            "sub": "testuser",
            "scopes": ["read", "write"]
            # Sin user_id
        }
        
        handler = GetCurrentUserQueryHandler(
            mock_user_repository,
            mock_token_service
        )
        
        query = GetCurrentUserQuery(token="token_sin_user_id")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Token inválido"):
            await handler.handle(query)
    
    async def test_handle_usuario_no_existe(
        self,
        mock_user_repository,
        mock_token_service
    ):
        """Test: Usuario no existe en la base de datos"""
        # Arrange
        expected_payload = {
            "sub": "testuser",
            "user_id": "nonexistent",
            "scopes": ["read", "write"]
        }
        mock_token_service.verify_access_token.return_value = expected_payload
        mock_user_repository.find_by_id.return_value = None
        
        handler = GetCurrentUserQueryHandler(
            mock_user_repository,
            mock_token_service
        )
        
        query = GetCurrentUserQuery(token="valid_token")
        
        # Act
        result = await handler.handle(query)
        
        # Assert
        assert result is None
        mock_token_service.verify_access_token.assert_called_once_with("valid_token")
        mock_user_repository.find_by_id.assert_called_once_with(EntityId("nonexistent"))
