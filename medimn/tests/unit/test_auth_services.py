"""
Tests unitarios para Auth Services (Event Handlers)
"""
import pytest
from unittest.mock import AsyncMock, Mock
from auth.application.services import UserEventHandler


@pytest.mark.unit
class TestUserEventHandler:
    """Tests para UserEventHandler"""
    
    @pytest.mark.asyncio
    async def test_handle_user_registered_event(self):
        """Test manejar evento UserRegistered"""
        handler = UserEventHandler()
        
        from auth.domain.events import UserRegisteredEvent
        
        event = UserRegisteredEvent(
            user_id="test-user-id",
            email="test@example.com",
            username="testuser"
        )
        
        # El handler debería procesar el evento sin errores
        await handler.on_user_registered(event)
    
    @pytest.mark.asyncio
    async def test_handle_user_logged_in_event(self):
        """Test manejar evento UserLoggedIn"""
        handler = UserEventHandler()
        
        from auth.domain.events import UserLoggedInEvent
        
        event = UserLoggedInEvent(
            user_id="test-user-id",
            username="testuser"
        )
        
        # El handler debería procesar el evento sin errores
        await handler.on_user_logged_in(event)

