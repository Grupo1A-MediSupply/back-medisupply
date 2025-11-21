"""
Tests adicionales para Auth Handlers para aumentar cobertura
"""
import pytest
from unittest.mock import AsyncMock, Mock
from auth.application.handlers import (
    DeactivateUserCommandHandler,
    UpdateProfileCommandHandler,
    GetUserByEmailQueryHandler,
    GetCurrentUserQueryHandler
)
from auth.application.commands import (
    DeactivateUserCommand,
    UpdateProfileCommand
)
from auth.application.queries import (
    GetUserByEmailQuery,
    GetCurrentUserQuery
)
from shared.domain.value_objects import EntityId, Email


@pytest.mark.unit
class TestDeactivateUserCommandHandler:
    """Tests adicionales para DeactivateUserCommandHandler"""
    
    @pytest.mark.asyncio
    async def test_deactivate_user_success(self, mock_user_repository, sample_user_entity):
        """Test desactivar usuario exitoso"""
        handler = DeactivateUserCommandHandler(mock_user_repository)
        
        sample_user_entity.deactivate = Mock()
        sample_user_entity.get_domain_events = Mock(return_value=[])
        sample_user_entity.clear_domain_events = Mock()
        
        mock_user_repository.find_by_id = AsyncMock(return_value=sample_user_entity)
        mock_user_repository.save = AsyncMock(return_value=sample_user_entity)
        
        command = DeactivateUserCommand(user_id=str(sample_user_entity.id))
        
        result = await handler.handle(command)
        
        assert result is not None
        sample_user_entity.deactivate.assert_called_once()
        mock_user_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_deactivate_user_not_found(self, mock_user_repository):
        """Test desactivar usuario no encontrado"""
        handler = DeactivateUserCommandHandler(mock_user_repository)
        
        mock_user_repository.find_by_id = AsyncMock(return_value=None)
        
        command = DeactivateUserCommand(user_id="nonexistent-id")
        
        with pytest.raises(ValueError, match="Usuario no encontrado"):
            await handler.handle(command)


@pytest.mark.unit
class TestUpdateProfileCommandHandler:
    """Tests adicionales para UpdateProfileCommandHandler"""
    
    @pytest.mark.asyncio
    async def test_update_profile_success(self, mock_user_repository, sample_user_entity):
        """Test actualizar perfil exitoso"""
        handler = UpdateProfileCommandHandler(mock_user_repository)
        
        sample_user_entity.update_profile = Mock()
        mock_user_repository.find_by_id = AsyncMock(return_value=sample_user_entity)
        mock_user_repository.save = AsyncMock(return_value=sample_user_entity)
        
        command = UpdateProfileCommand(
            user_id=str(sample_user_entity.id),
            full_name="New Name",
            phone_number="+1234567890"
        )
        
        result = await handler.handle(command)
        
        assert result is not None
        sample_user_entity.update_profile.assert_called_once()
        mock_user_repository.save.assert_called_once()


@pytest.mark.unit
class TestGetUserByEmailQueryHandler:
    """Tests adicionales para GetUserByEmailQueryHandler"""
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, mock_user_repository, sample_user_entity):
        """Test obtener usuario por email exitoso"""
        handler = GetUserByEmailQueryHandler(mock_user_repository)
        
        mock_user_repository.find_by_email = AsyncMock(return_value=sample_user_entity)
        
        query = GetUserByEmailQuery(email="test@example.com")
        
        result = await handler.handle(query)
        
        assert result == sample_user_entity
        mock_user_repository.find_by_email.assert_called_once()


@pytest.mark.unit
class TestGetCurrentUserQueryHandler:
    """Tests adicionales para GetCurrentUserQueryHandler"""
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, mock_user_repository, mock_token_service, sample_user_entity):
        """Test obtener usuario actual exitoso"""
        handler = GetCurrentUserQueryHandler(mock_user_repository, mock_token_service)
        
        mock_token_service.verify_access_token = Mock(return_value={"user_id": str(sample_user_entity.id)})
        mock_user_repository.find_by_id = AsyncMock(return_value=sample_user_entity)
        
        query = GetCurrentUserQuery(token="valid_token")
        
        result = await handler.handle(query)
        
        assert result == sample_user_entity
        mock_token_service.verify_access_token.assert_called_once()
        mock_user_repository.find_by_id.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, mock_user_repository, mock_token_service):
        """Test obtener usuario actual con token inválido"""
        handler = GetCurrentUserQueryHandler(mock_user_repository, mock_token_service)
        
        mock_token_service.verify_access_token = Mock(return_value={})  # Sin user_id
        
        query = GetCurrentUserQuery(token="invalid_token")
        
        with pytest.raises(ValueError, match="Token inválido"):
            await handler.handle(query)

