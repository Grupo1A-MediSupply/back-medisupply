"""
Tests unitarios para Command Handlers
"""
import pytest
from uuid import uuid4
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, Mock

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
            confirm_password="Password123!",
            full_name="Test User",
            phone_number="+1234567890"
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
            password="Password123!",
            confirm_password="Password123!"
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
            password="Password123!",
            confirm_password="Password123!"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="ya está registrado"):
            await handler.handle(command)
        
        mock_user_repository.save.assert_not_called()

    async def test_handle_falla_si_contraseñas_no_coinciden(
        self,
        mock_user_repository,
        mock_password_hasher
    ):
        """Test: Fallar si las contraseñas no coinciden"""
        # Arrange
        handler = RegisterUserCommandHandler(
            mock_user_repository,
            mock_password_hasher
        )
        
        command = RegisterUserCommand(
            email="test@example.com",
            username="testuser",
            password="Password123!",
            confirm_password="DifferentPassword123!"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Las contraseñas no coinciden"):
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
        mock_verification_code_repository,
        mock_email_service
    ):
        """Test: Login exitoso con username"""
        from application.commands import LoginCommand
        from application.handlers import LoginCommandHandler
        
        # Arrange
        mock_user_repository.find_by_username.return_value = user
        mock_password_hasher.verify_password.return_value = True
        mock_verification_code_repository.create_verification_code.return_value = Mock()
        
        handler = LoginCommandHandler(
            mock_user_repository,
            mock_password_hasher,
            mock_verification_code_repository,
            mock_email_service
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
        assert result["message"] == "Código de verificación enviado al email"
        assert result["user_id"] == str(user.id)
        assert result["requires_verification"] is True
        mock_user_repository.find_by_username.assert_called_once()
        mock_password_hasher.verify_password.assert_called_once()
        mock_email_service.send_verification_code.assert_called_once()
    
    async def test_handle_login_fallido_usuario_no_existe(
        self,
        mock_user_repository,
        mock_password_hasher,
        mock_verification_code_repository,
        mock_email_service
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
            mock_verification_code_repository,
            mock_email_service
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
        mock_verification_code_repository,
        mock_email_service
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
            mock_verification_code_repository,
            mock_email_service
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
        mock_verification_code_repository,
        mock_email_service
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
            mock_verification_code_repository,
            mock_email_service
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


@pytest.mark.unit
@pytest.mark.asyncio
class TestChangePasswordCommandHandler:
    """Tests para ChangePasswordCommandHandler"""
    
    async def test_handle_cambia_contraseña_exitosamente(
        self,
        user,
        mock_user_repository,
        mock_password_hasher
    ):
        """Test: Cambiar contraseña exitosamente"""
        # Arrange
        mock_user_repository.find_by_id.return_value = user
        mock_password_hasher.verify_password.return_value = True
        mock_user_repository.save.return_value = user
        
        handler = ChangePasswordCommandHandler(
            mock_user_repository,
            mock_password_hasher
        )
        
        command = ChangePasswordCommand(
            user_id="123",
            old_password="OldPassword123!",
            new_password="NewPassword123!"
        )
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result == user
        mock_user_repository.find_by_id.assert_called_once()
        mock_password_hasher.verify_password.assert_called_once()
        mock_password_hasher.hash_password.assert_called_once_with("NewPassword123!")
        mock_user_repository.save.assert_called_once()
    
    async def test_handle_falla_si_usuario_no_existe(
        self,
        mock_user_repository,
        mock_password_hasher
    ):
        """Test: Falla si usuario no existe"""
        # Arrange
        mock_user_repository.find_by_id.return_value = None
        
        handler = ChangePasswordCommandHandler(
            mock_user_repository,
            mock_password_hasher
        )
        
        command = ChangePasswordCommand(
            user_id="nonexistent",
            old_password="OldPassword123!",
            new_password="NewPassword123!"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="no encontrado"):
            await handler.handle(command)
    
    async def test_handle_falla_si_contraseña_actual_incorrecta(
        self,
        user,
        mock_user_repository,
        mock_password_hasher
    ):
        """Test: Falla si contraseña actual es incorrecta"""
        # Arrange
        mock_user_repository.find_by_id.return_value = user
        mock_password_hasher.verify_password.return_value = False
        
        handler = ChangePasswordCommandHandler(
            mock_user_repository,
            mock_password_hasher
        )
        
        command = ChangePasswordCommand(
            user_id="123",
            old_password="WrongPassword",
            new_password="NewPassword123!"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Contraseña actual incorrecta"):
            await handler.handle(command)


@pytest.mark.unit
@pytest.mark.asyncio
class TestDeactivateUserCommandHandler:
    """Tests para DeactivateUserCommandHandler"""
    
    async def test_handle_desactiva_usuario_exitosamente(
        self,
        user,
        mock_user_repository
    ):
        """Test: Desactivar usuario exitosamente"""
        # Arrange
        mock_user_repository.find_by_id.return_value = user
        mock_user_repository.save.return_value = user
        
        handler = DeactivateUserCommandHandler(mock_user_repository)
        
        command = DeactivateUserCommand(user_id="123")
        
        # Act
        with patch('application.handlers.event_bus') as mock_event_bus:
            mock_event_bus.publish = AsyncMock()
            result = await handler.handle(command)
        
        # Assert
        assert result == user
        assert user.is_active is False
        mock_user_repository.find_by_id.assert_called_once()
        mock_user_repository.save.assert_called_once()
    
    async def test_handle_falla_si_usuario_no_existe(
        self,
        mock_user_repository
    ):
        """Test: Falla si usuario no existe"""
        # Arrange
        mock_user_repository.find_by_id.return_value = None
        
        handler = DeactivateUserCommandHandler(mock_user_repository)
        
        command = DeactivateUserCommand(user_id="nonexistent")
        
        # Act & Assert
        with pytest.raises(ValueError, match="no encontrado"):
            await handler.handle(command)


@pytest.mark.unit
@pytest.mark.asyncio
class TestUpdateProfileCommandHandler:
    """Tests para UpdateProfileCommandHandler"""
    
    async def test_handle_actualiza_perfil_exitosamente(
        self,
        user,
        mock_user_repository
    ):
        """Test: Actualizar perfil exitosamente"""
        # Arrange
        mock_user_repository.find_by_id.return_value = user
        mock_user_repository.save.return_value = user
        
        handler = UpdateProfileCommandHandler(mock_user_repository)
        
        command = UpdateProfileCommand(
            user_id="123",
            full_name="New Name",
            phone_number="+1234567890"
        )
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result == user
        assert str(user.full_name) == "New Name"
        assert str(user.phone_number) == "+1234567890"
        mock_user_repository.find_by_id.assert_called_once()
        mock_user_repository.save.assert_called_once()
    
    async def test_handle_falla_si_usuario_no_existe(
        self,
        mock_user_repository
    ):
        """Test: Falla si usuario no existe"""
        # Arrange
        mock_user_repository.find_by_id.return_value = None
        
        handler = UpdateProfileCommandHandler(mock_user_repository)
        
        command = UpdateProfileCommand(
            user_id="nonexistent",
            full_name="New Name"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="no encontrado"):
            await handler.handle(command)


@pytest.mark.unit
@pytest.mark.asyncio
class TestVerifyCodeCommandHandler:
    """Tests para VerifyCodeCommandHandler"""
    
    async def test_handle_verifica_codigo_exitosamente(
        self,
        mock_verification_code_repository,
        mock_token_service
    ):
        """Test: Verificar código exitosamente"""
        # Arrange
        mock_verification_code = Mock()
        mock_verification_code.user_id = "123"
        mock_verification_code_repository.get_valid_code.return_value = mock_verification_code
        mock_verification_code_repository.mark_code_as_used.return_value = None
        
        handler = VerifyCodeCommandHandler(
            mock_verification_code_repository,
            mock_token_service
        )
        
        command = VerifyCodeCommand(
            user_id="123",
            code="123456"
        )
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        mock_verification_code_repository.get_valid_code.assert_called_once_with("123", "123456")
        mock_verification_code_repository.mark_code_as_used.assert_called_once_with(mock_verification_code)
    
    async def test_handle_falla_si_codigo_invalido(
        self,
        mock_verification_code_repository,
        mock_token_service
    ):
        """Test: Falla si código es inválido"""
        # Arrange
        mock_verification_code_repository.get_valid_code.return_value = None
        
        handler = VerifyCodeCommandHandler(
            mock_verification_code_repository,
            mock_token_service
        )
        
        command = VerifyCodeCommand(
            user_id="123",
            code="invalid"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Código inválido o expirado"):
            await handler.handle(command)

