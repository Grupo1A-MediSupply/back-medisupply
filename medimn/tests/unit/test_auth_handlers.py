"""
Tests unitarios para Auth Handlers
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from auth.application.handlers import (
    RegisterUserCommandHandler,
    LoginCommandHandler,
    RefreshTokenCommandHandler,
    ChangePasswordCommandHandler,
    DeactivateUserCommandHandler,
    UpdateProfileCommandHandler,
    GetUserByIdQueryHandler,
    GetUserByUsernameQueryHandler,
    GetCurrentUserQueryHandler,
    VerifyTokenQueryHandler,
    VerifyCodeCommandHandler
)
from auth.application.commands import (
    RegisterUserCommand,
    LoginCommand,
    RefreshTokenCommand,
    ChangePasswordCommand,
    DeactivateUserCommand,
    UpdateProfileCommand,
    VerifyCodeCommand
)
from auth.application.queries import (
    GetUserByIdQuery,
    GetUserByUsernameQuery,
    GetCurrentUserQuery,
    VerifyTokenQuery
)
from shared.domain.value_objects import EntityId, Email
from auth.domain.value_objects import Username


@pytest.mark.unit
class TestRegisterUserCommandHandler:
    """Tests para RegisterUserCommandHandler"""
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, mock_user_repository, mock_password_hasher, sample_user_data):
        """Test registro exitoso de usuario"""
        handler = RegisterUserCommandHandler(mock_user_repository, mock_password_hasher)
        
        command = RegisterUserCommand(**sample_user_data)
        
        # Mock del usuario guardado
        from auth.domain.entities import User
        from auth.domain.value_objects import HashedPassword
        saved_user = Mock(spec=User)
        saved_user.get_domain_events = Mock(return_value=[])
        saved_user.clear_domain_events = Mock()
        mock_user_repository.save = AsyncMock(return_value=saved_user)
        
        result = await handler.handle(command)
        
        assert result is not None
        mock_user_repository.exists_by_username.assert_called_once()
        mock_user_repository.exists_by_email.assert_called_once()
        mock_password_hasher.hash_password.assert_called_once()
        mock_user_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_user_password_mismatch(self, mock_user_repository, mock_password_hasher):
        """Test registro con contraseñas que no coinciden"""
        handler = RegisterUserCommandHandler(mock_user_repository, mock_password_hasher)
        
        command = RegisterUserCommand(
            email="test@example.com",
            username="testuser",
            password="password123",
            confirm_password="different123"
        )
        
        with pytest.raises(ValueError, match="Las contraseñas no coinciden"):
            await handler.handle(command)
    
    @pytest.mark.asyncio
    async def test_register_user_username_exists(self, mock_user_repository, mock_password_hasher):
        """Test registro con username ya existente"""
        mock_user_repository.exists_by_username = AsyncMock(return_value=True)
        
        handler = RegisterUserCommandHandler(mock_user_repository, mock_password_hasher)
        
        command = RegisterUserCommand(
            email="test@example.com",
            username="existinguser",
            password="password123",
            confirm_password="password123"
        )
        
        with pytest.raises(ValueError, match="ya está registrado"):
            await handler.handle(command)
    
    @pytest.mark.asyncio
    async def test_register_user_email_exists(self, mock_user_repository, mock_password_hasher):
        """Test registro con email ya existente"""
        mock_user_repository.exists_by_username = AsyncMock(return_value=False)
        mock_user_repository.exists_by_email = AsyncMock(return_value=True)
        
        handler = RegisterUserCommandHandler(mock_user_repository, mock_password_hasher)
        
        command = RegisterUserCommand(
            email="existing@example.com",
            username="newuser",
            password="password123",
            confirm_password="password123"
        )
        
        with pytest.raises(ValueError, match="ya está registrado"):
            await handler.handle(command)


@pytest.mark.unit
class TestLoginCommandHandler:
    """Tests para LoginCommandHandler"""
    
    @pytest.mark.asyncio
    async def test_login_success(self, mock_user_repository, mock_password_hasher, mock_token_service, sample_user_entity):
        """Test login exitoso (sin MFA)"""
        handler = LoginCommandHandler(
            mock_user_repository,
            mock_password_hasher,
            mock_token_service
        )
        
        mock_user_repository.find_by_username = AsyncMock(return_value=sample_user_entity)
        mock_password_hasher.verify_password = Mock(return_value=True)
        
        command = LoginCommand(username="testuser", password="testpass123")
        
        result = await handler.handle(command)
        
        assert result is not None
        assert "message" in result
        assert "access_token" in result
        assert "refresh_token" in result
        assert "token_type" in result
        assert "user" in result
        assert result["requires_verification"] is False
        mock_user_repository.find_by_username.assert_called_once()
        mock_password_hasher.verify_password.assert_called_once()
        mock_token_service.create_access_token.assert_called_once()
        mock_token_service.create_refresh_token.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_login_user_not_found(self, mock_user_repository, mock_password_hasher, mock_token_service):
        """Test login con usuario no encontrado"""
        handler = LoginCommandHandler(
            mock_user_repository,
            mock_password_hasher,
            mock_token_service
        )
        
        mock_user_repository.find_by_username = AsyncMock(return_value=None)
        mock_user_repository.find_by_email = AsyncMock(return_value=None)
        
        command = LoginCommand(username="nonexistent", password="testpass123")
        
        with pytest.raises(ValueError, match="Credenciales incorrectas"):
            await handler.handle(command)
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, mock_user_repository, mock_password_hasher, mock_token_service, sample_user_entity):
        """Test login con contraseña incorrecta"""
        handler = LoginCommandHandler(
            mock_user_repository,
            mock_password_hasher,
            mock_token_service
        )
        
        mock_user_repository.find_by_username = AsyncMock(return_value=sample_user_entity)
        mock_password_hasher.verify_password = Mock(return_value=False)
        
        command = LoginCommand(username="testuser", password="wrongpassword")
        
        with pytest.raises(ValueError, match="Credenciales incorrectas"):
            await handler.handle(command)


@pytest.mark.unit
class TestRefreshTokenCommandHandler:
    """Tests para RefreshTokenCommandHandler"""
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, mock_user_repository, mock_token_service, sample_user_entity):
        """Test refresh token exitoso"""
        handler = RefreshTokenCommandHandler(mock_user_repository, mock_token_service)
        
        mock_token_service.verify_refresh_token = Mock(return_value={"user_id": str(sample_user_entity.id)})
        mock_user_repository.find_by_id = AsyncMock(return_value=sample_user_entity)
        
        command = RefreshTokenCommand(refresh_token="valid_refresh_token")
        
        result = await handler.handle(command)
        
        assert "access_token" in result
        assert "refresh_token" in result
        assert "token_type" in result
        mock_token_service.verify_refresh_token.assert_called_once()
        mock_token_service.create_access_token.assert_called_once()
        mock_token_service.create_refresh_token.assert_called_once()


@pytest.mark.unit
class TestChangePasswordCommandHandler:
    """Tests para ChangePasswordCommandHandler"""
    
    @pytest.mark.asyncio
    async def test_change_password_success(self, mock_user_repository, mock_password_hasher, sample_user_entity):
        """Test cambio de contraseña exitoso"""
        handler = ChangePasswordCommandHandler(mock_user_repository, mock_password_hasher)
        
        # Mock del usuario con método change_password
        sample_user_entity.change_password = Mock()
        mock_user_repository.find_by_id = AsyncMock(return_value=sample_user_entity)
        mock_password_hasher.verify_password = Mock(return_value=True)
        mock_password_hasher.hash_password = Mock(return_value="$2b$12$newhashedpassword")
        mock_user_repository.save = AsyncMock(return_value=sample_user_entity)
        
        command = ChangePasswordCommand(
            user_id=str(sample_user_entity.id),
            current_password="oldpass",
            new_password="newpass",
            confirm_new_password="newpass"
        )
        
        result = await handler.handle(command)
        
        assert result is not None
        mock_password_hasher.verify_password.assert_called_once()
        mock_password_hasher.hash_password.assert_called_once()
        sample_user_entity.change_password.assert_called_once()
        mock_user_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_change_password_wrong_old_password(self, mock_user_repository, mock_password_hasher, sample_user_entity):
        """Test cambio de contraseña con contraseña antigua incorrecta"""
        handler = ChangePasswordCommandHandler(mock_user_repository, mock_password_hasher)
        
        mock_user_repository.find_by_id = AsyncMock(return_value=sample_user_entity)
        mock_password_hasher.verify_password = Mock(return_value=False)
        
        command = ChangePasswordCommand(
            user_id=str(sample_user_entity.id),
            current_password="wrongoldpass",
            new_password="newpass",
            confirm_new_password="newpass"
        )
        
        with pytest.raises(ValueError, match="Contraseña actual incorrecta"):
            await handler.handle(command)


@pytest.mark.unit
class TestGetUserByIdQueryHandler:
    """Tests para GetUserByIdQueryHandler"""
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, mock_user_repository, sample_user_entity):
        """Test obtener usuario por ID exitoso"""
        handler = GetUserByIdQueryHandler(mock_user_repository)
        
        mock_user_repository.find_by_id = AsyncMock(return_value=sample_user_entity)
        
        query = GetUserByIdQuery(user_id=str(sample_user_entity.id))
        
        result = await handler.handle(query)
        
        assert result == sample_user_entity
        mock_user_repository.find_by_id.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, mock_user_repository):
        """Test obtener usuario por ID no encontrado"""
        handler = GetUserByIdQueryHandler(mock_user_repository)
        
        mock_user_repository.find_by_id = AsyncMock(return_value=None)
        
        query = GetUserByIdQuery(user_id="nonexistent-id")
        
        result = await handler.handle(query)
        
        assert result is None


@pytest.mark.unit
class TestGetUserByUsernameQueryHandler:
    """Tests para GetUserByUsernameQueryHandler"""
    
    @pytest.mark.asyncio
    async def test_get_user_by_username_success(self, mock_user_repository, sample_user_entity):
        """Test obtener usuario por username exitoso"""
        handler = GetUserByUsernameQueryHandler(mock_user_repository)
        
        mock_user_repository.find_by_username = AsyncMock(return_value=sample_user_entity)
        
        query = GetUserByUsernameQuery(username="testuser")
        
        result = await handler.handle(query)
        
        assert result == sample_user_entity
        mock_user_repository.find_by_username.assert_called_once()


@pytest.mark.unit
class TestVerifyTokenQueryHandler:
    """Tests para VerifyTokenQueryHandler"""
    
    @pytest.mark.asyncio
    async def test_verify_token_success(self, mock_token_service):
        """Test verificación de token exitosa"""
        handler = VerifyTokenQueryHandler(mock_token_service)
        
        mock_token_service.verify_access_token = Mock(return_value={"user_id": "test_id", "sub": "testuser"})
        
        query = VerifyTokenQuery(token="valid_token")
        
        result = await handler.handle(query)
        
        assert result is not None
        assert result["valid"] is True
        assert "payload" in result
        mock_token_service.verify_access_token.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_verify_token_invalid(self, mock_token_service):
        """Test verificación de token inválido"""
        handler = VerifyTokenQueryHandler(mock_token_service)
        
        mock_token_service.verify_access_token = Mock(side_effect=ValueError("Token inválido"))
        
        query = VerifyTokenQuery(token="invalid_token")
        
        result = await handler.handle(query)
        
        assert result is not None
        assert result["valid"] is False
        assert "error" in result

