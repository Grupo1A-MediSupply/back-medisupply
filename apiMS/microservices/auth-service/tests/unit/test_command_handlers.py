"""
Tests unitarios para Command Handlers
"""
import pytest
from uuid import uuid4
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Agregar paths
auth_service_path = str(Path(__file__).parent.parent.resolve())
shared_path = str(Path(__file__).parent.parent.parent.resolve() / "shared")
if auth_service_path not in sys.path:
    sys.path.insert(0, auth_service_path)
if shared_path not in sys.path:
    sys.path.insert(0, str(shared_path))

# Los imports se hacen dentro de las clases para evitar problemas cuando pytest carga el módulo


@pytest.mark.unit
@pytest.mark.asyncio
class TestRegisterUserCommandHandler:
    """Tests para RegisterUserCommandHandler"""
    
    async def test_handle_registra_usuario_exitosamente(
        self,
        mock_user_repository,
        mock_password_hasher
    ):
        """Test: Registrar usuario exitosamente"""
        # Los imports se hacen aquí para evitar problemas cuando pytest carga el módulo
        from shared.domain.value_objects import EntityId, Email
        from domain.value_objects import Username, HashedPassword
        from domain.entities import User
        from application.commands import RegisterUserCommand
        from application.handlers import RegisterUserCommandHandler
        
        # Arrange
        handler = RegisterUserCommandHandler(
            mock_user_repository,
            mock_password_hasher
        )
        
        command = RegisterUserCommand(
            email="test@example.com",
            username="testuser",
            password="Password123!",
            full_name="Test User"
        )
        
        # Mock del usuario guardado
        expected_user = User(
            user_id=EntityId(str(uuid4())),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("$2b$12$hashed_password")
        )
        mock_user_repository.save.return_value = expected_user
        
        # Act
        with patch('application.handlers.event_bus') as mock_event_bus:
            mock_event_bus.publish = AsyncMock()
            result = await handler.handle(command)
        
        # Assert
        assert result is not None
        mock_user_repository.exists_by_username.assert_called_once()
        mock_user_repository.exists_by_email.assert_called_once()
        mock_password_hasher.hash_password.assert_called_once_with("Password123!")
        mock_user_repository.save.assert_called_once()
    
    async def test_handle_falla_si_username_existe(
        self,
        mock_user_repository,
        mock_password_hasher
    ):
        """Test: Falla si el username ya existe"""
        from application.commands import RegisterUserCommand
        from application.handlers import RegisterUserCommandHandler
        
        # Arrange
        mock_user_repository.exists_by_username.return_value = True
        
        handler = RegisterUserCommandHandler(
            mock_user_repository,
            mock_password_hasher
        )
        
        command = RegisterUserCommand(
            email="test@example.com",
            username="testuser",
            password="Password123!"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="ya está registrado"):
            await handler.handle(command)
        
        mock_user_repository.save.assert_not_called()
    
    async def test_handle_falla_si_email_existe(
        self,
        mock_user_repository,
        mock_password_hasher
    ):
        """Test: Falla si el email ya existe"""
        from application.commands import RegisterUserCommand
        from application.handlers import RegisterUserCommandHandler
        
        # Arrange
        mock_user_repository.exists_by_username.return_value = False
        mock_user_repository.exists_by_email.return_value = True
        
        handler = RegisterUserCommandHandler(
            mock_user_repository,
            mock_password_hasher
        )
        
        command = RegisterUserCommand(
            email="test@example.com",
            username="testuser",
            password="Password123!"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="ya está registrado"):
            await handler.handle(command)
        
        mock_user_repository.save.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
class TestLoginCommandHandler:
    """Tests para LoginCommandHandler"""
    
    async def test_handle_login_exitoso_con_username(
        self,
        user,
        mock_user_repository,
        mock_password_hasher,
        mock_token_service
    ):
        """Test: Login exitoso con username"""
        from application.commands import LoginCommand
        from application.handlers import LoginCommandHandler
        
        # Arrange
        mock_user_repository.find_by_username.return_value = user
        mock_password_hasher.verify_password.return_value = True
        
        handler = LoginCommandHandler(
            mock_user_repository,
            mock_password_hasher,
            mock_token_service
        )
        
        command = LoginCommand(
            username="testuser",
            password="Password123!"
        )
        
        # Act
        with patch('application.handlers.event_bus') as mock_event_bus:
            mock_event_bus.publish = AsyncMock()
            result = await handler.handle(command)
        
        # Assert
        assert result["access_token"] == "access_token_123"
        assert result["refresh_token"] == "refresh_token_123"
        assert result["token_type"] == "bearer"
        mock_user_repository.find_by_username.assert_called_once()
        mock_password_hasher.verify_password.assert_called_once()
    
    async def test_handle_login_fallido_usuario_no_existe(
        self,
        mock_user_repository,
        mock_password_hasher,
        mock_token_service
    ):
        """Test: Login falla si usuario no existe"""
        from application.commands import LoginCommand
        from application.handlers import LoginCommandHandler
        
        # Arrange
        mock_user_repository.find_by_username.return_value = None
        mock_user_repository.find_by_email.return_value = None
        
        handler = LoginCommandHandler(
            mock_user_repository,
            mock_password_hasher,
            mock_token_service
        )
        
        command = LoginCommand(
            username="noexiste",
            password="Password123!"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="incorrectas"):
            await handler.handle(command)
    
    async def test_handle_login_fallido_password_incorrecto(
        self,
        user,
        mock_user_repository,
        mock_password_hasher,
        mock_token_service
    ):
        """Test: Login falla si contraseña es incorrecta"""
        from application.commands import LoginCommand
        from application.handlers import LoginCommandHandler
        
        # Arrange
        mock_user_repository.find_by_username.return_value = user
        mock_password_hasher.verify_password.return_value = False
        
        handler = LoginCommandHandler(
            mock_user_repository,
            mock_password_hasher,
            mock_token_service
        )
        
        command = LoginCommand(
            username="testuser",
            password="WrongPassword"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="incorrectas"):
            await handler.handle(command)
    
    async def test_handle_login_fallido_usuario_inactivo(
        self,
        mock_user_repository,
        mock_password_hasher,
        mock_token_service
    ):
        """Test: Login falla si usuario está inactivo"""
        from shared.domain.value_objects import EntityId, Email
        from domain.value_objects import Username, HashedPassword
        from domain.entities import User
        from application.commands import LoginCommand
        from application.handlers import LoginCommandHandler
        
        # Arrange
        inactive_user = User(
            user_id=EntityId("123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("$2b$12$hash"),
            is_active=False
        )
        
        mock_user_repository.find_by_username.return_value = inactive_user
        mock_password_hasher.verify_password.return_value = True
        
        handler = LoginCommandHandler(
            mock_user_repository,
            mock_password_hasher,
            mock_token_service
        )
        
        command = LoginCommand(
            username="testuser",
            password="Password123!"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="desactivado"):
            await handler.handle(command)


@pytest.mark.unit
@pytest.mark.asyncio
class TestRefreshTokenCommandHandler:
    """Tests para RefreshTokenCommandHandler"""
    
    async def test_handle_refresh_token_exitoso(
        self,
        user,
        mock_user_repository,
        mock_token_service
    ):
        """Test: Refresh token exitoso"""
        from application.commands import RefreshTokenCommand
        from application.handlers import RefreshTokenCommandHandler
        
        # Arrange
        mock_user_repository.find_by_id.return_value = user
        mock_token_service.verify_refresh_token.return_value = {
            "user_id": str(user.id),
            "sub": str(user.username)
        }
        
        handler = RefreshTokenCommandHandler(
            mock_user_repository,
            mock_token_service
        )
        
        command = RefreshTokenCommand(refresh_token="refresh_token_123")
        
        # Act
        with patch('application.handlers.event_bus') as mock_event_bus:
            mock_event_bus.publish = AsyncMock()
            result = await handler.handle(command)
        
        # Assert
        assert result["access_token"] == "access_token_123"
        assert result["refresh_token"] == "refresh_token_123"
        mock_token_service.verify_refresh_token.assert_called_once()
        mock_user_repository.find_by_id.assert_called_once()
    
    async def test_handle_refresh_token_invalido(
        self,
        mock_user_repository,
        mock_token_service
    ):
        """Test: Refresh token inválido lanza error"""
        from application.commands import RefreshTokenCommand
        from application.handlers import RefreshTokenCommandHandler
        
        # Arrange
        mock_token_service.verify_refresh_token.side_effect = ValueError("Token inválido")
        
        handler = RefreshTokenCommandHandler(
            mock_user_repository,
            mock_token_service
        )
        
        command = RefreshTokenCommand(refresh_token="invalid_token")
        
        # Act & Assert
        with pytest.raises(ValueError):
            await handler.handle(command)
    
    async def test_handle_refresh_token_usuario_no_existe(
        self,
        mock_user_repository,
        mock_token_service
    ):
        """Test: Refresh token falla si usuario no existe"""
        from application.commands import RefreshTokenCommand
        from application.handlers import RefreshTokenCommandHandler
        
        # Arrange
        mock_token_service.verify_refresh_token.return_value = {
            "user_id": "nonexistent",
            "sub": "testuser"
        }
        mock_user_repository.find_by_id.return_value = None
        
        handler = RefreshTokenCommandHandler(
            mock_user_repository,
            mock_token_service
        )
        
        command = RefreshTokenCommand(refresh_token="refresh_token_123")
        
        # Act & Assert
        with pytest.raises(ValueError, match="no encontrado"):
            await handler.handle(command)

