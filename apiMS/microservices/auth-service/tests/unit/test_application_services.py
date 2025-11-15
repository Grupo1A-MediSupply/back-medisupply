"""
Tests unitarios para servicios de aplicación (event handlers)
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

# Agregar paths
auth_service_path = str(Path(__file__).parent.parent.parent)
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if auth_service_path not in sys.path:
    sys.path.insert(0, auth_service_path)
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from domain.events import UserRegisteredEvent, UserLoggedInEvent, UserDeactivatedEvent
from application.services import UserEventHandler, setup_event_handlers


@pytest.mark.unit
class TestUserEventHandler:
    """Tests para UserEventHandler"""
    
    def test_init(self):
        """Test: Inicialización del event handler"""
        handler = UserEventHandler()
        assert handler is not None
    
    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_on_user_registered(self, mock_print):
        """Test: Manejar evento de usuario registrado"""
        handler = UserEventHandler()
        event = UserRegisteredEvent(
            user_id="123",
            username="testuser",
            email="test@example.com"
        )
        
        await handler.on_user_registered(event)
        
        # Verificar que se imprimió el mensaje
        mock_print.assert_called_once_with(
            "📧 [EVENT] Usuario registrado: testuser (test@example.com)"
        )
    
    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_on_user_logged_in(self, mock_print):
        """Test: Manejar evento de usuario logueado"""
        handler = UserEventHandler()
        event = UserLoggedInEvent(
            user_id="123",
            username="testuser"
        )
        
        await handler.on_user_logged_in(event)
        
        # Verificar que se imprimió el mensaje
        mock_print.assert_called_once_with(
            "🔐 [EVENT] Usuario logueado: testuser"
        )
    
    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_on_user_deactivated(self, mock_print):
        """Test: Manejar evento de usuario desactivado"""
        handler = UserEventHandler()
        event = UserDeactivatedEvent(user_id="123")
        
        await handler.on_user_deactivated(event)
        
        # Verificar que se imprimió el mensaje
        mock_print.assert_called_once_with(
            "❌ [EVENT] Usuario desactivado: 123"
        )
    
    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_on_user_registered_with_different_data(self, mock_print):
        """Test: Manejar evento de usuario registrado con datos diferentes"""
        handler = UserEventHandler()
        event = UserRegisteredEvent(
            user_id="456",
            username="anotheruser",
            email="another@example.com"
        )
        
        await handler.on_user_registered(event)
        
        # Verificar que se imprimió el mensaje correcto
        mock_print.assert_called_once_with(
            "📧 [EVENT] Usuario registrado: anotheruser (another@example.com)"
        )
    
    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_on_user_logged_in_with_different_data(self, mock_print):
        """Test: Manejar evento de usuario logueado con datos diferentes"""
        handler = UserEventHandler()
        event = UserLoggedInEvent(
            user_id="456",
            username="anotheruser"
        )
        
        await handler.on_user_logged_in(event)
        
        # Verificar que se imprimió el mensaje correcto
        mock_print.assert_called_once_with(
            "🔐 [EVENT] Usuario logueado: anotheruser"
        )
    
    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_on_user_deactivated_with_different_data(self, mock_print):
        """Test: Manejar evento de usuario desactivado con datos diferentes"""
        handler = UserEventHandler()
        event = UserDeactivatedEvent(user_id="456")
        
        await handler.on_user_deactivated(event)
        
        # Verificar que se imprimió el mensaje correcto
        mock_print.assert_called_once_with(
            "❌ [EVENT] Usuario desactivado: 456"
        )
    
    @pytest.mark.asyncio
    async def test_on_user_registered_event_properties(self):
        """Test: Verificar propiedades del evento de usuario registrado"""
        handler = UserEventHandler()
        event = UserRegisteredEvent(
            user_id="123",
            username="testuser",
            email="test@example.com"
        )
        
        # Verificar que el evento tiene las propiedades correctas
        assert event.user_id == "123"
        assert event.username == "testuser"
        assert event.email == "test@example.com"
        
        # El handler debe poder procesar el evento sin errores
        await handler.on_user_registered(event)
    
    @pytest.mark.asyncio
    async def test_on_user_logged_in_event_properties(self):
        """Test: Verificar propiedades del evento de usuario logueado"""
        handler = UserEventHandler()
        event = UserLoggedInEvent(
            user_id="123",
            username="testuser"
        )
        
        # Verificar que el evento tiene las propiedades correctas
        assert event.user_id == "123"
        assert event.username == "testuser"
        
        # El handler debe poder procesar el evento sin errores
        await handler.on_user_logged_in(event)
    
    @pytest.mark.asyncio
    async def test_on_user_deactivated_event_properties(self):
        """Test: Verificar propiedades del evento de usuario desactivado"""
        handler = UserEventHandler()
        event = UserDeactivatedEvent(user_id="123")
        
        # Verificar que el evento tiene las propiedades correctas
        assert event.user_id == "123"
        
        # El handler debe poder procesar el evento sin errores
        await handler.on_user_deactivated(event)


@pytest.mark.unit
class TestSetupEventHandlers:
    """Tests para setup_event_handlers"""
    
    @patch('shared.domain.events.event_bus')
    def test_setup_event_handlers(self, mock_event_bus):
        """Test: Configurar handlers de eventos"""
        handler = UserEventHandler()
        
        setup_event_handlers(handler)
        
        # Verificar que se suscribieron todos los eventos
        assert mock_event_bus.subscribe.call_count == 3
        
        # Verificar las suscripciones específicas
        calls = mock_event_bus.subscribe.call_args_list
        
        # Verificar que se suscribió UserRegisteredEvent
        registered_call = next((call for call in calls if call[0][0] == "UserRegisteredEvent"), None)
        assert registered_call is not None
        assert registered_call[0][1] == handler.on_user_registered
        
        # Verificar que se suscribió UserLoggedInEvent
        logged_in_call = next((call for call in calls if call[0][0] == "UserLoggedInEvent"), None)
        assert logged_in_call is not None
        assert logged_in_call[0][1] == handler.on_user_logged_in
        
        # Verificar que se suscribió UserDeactivatedEvent
        deactivated_call = next((call for call in calls if call[0][0] == "UserDeactivatedEvent"), None)
        assert deactivated_call is not None
        assert deactivated_call[0][1] == handler.on_user_deactivated
    
    @patch('shared.domain.events.event_bus')
    def test_setup_event_handlers_with_different_handler(self, mock_event_bus):
        """Test: Configurar handlers de eventos con handler diferente"""
        handler = UserEventHandler()
        
        setup_event_handlers(handler)
        
        # Verificar que se suscribieron todos los eventos
        assert mock_event_bus.subscribe.call_count == 3
        
        # Verificar que se usó el handler correcto
        calls = mock_event_bus.subscribe.call_args_list
        for call in calls:
            assert call[0][1] == handler.on_user_registered or \
                   call[0][1] == handler.on_user_logged_in or \
                   call[0][1] == handler.on_user_deactivated
    
    @patch('shared.domain.events.event_bus')
    def test_setup_event_handlers_multiple_calls(self, mock_event_bus):
        """Test: Configurar handlers de eventos múltiples veces"""
        handler1 = UserEventHandler()
        handler2 = UserEventHandler()
        
        setup_event_handlers(handler1)
        setup_event_handlers(handler2)
        
        # Verificar que se suscribieron todos los eventos para ambos handlers
        assert mock_event_bus.subscribe.call_count == 6
        
        # Verificar que se usaron ambos handlers
        calls = mock_event_bus.subscribe.call_args_list
        handler1_calls = [call for call in calls if call[0][1] in [handler1.on_user_registered, handler1.on_user_logged_in, handler1.on_user_deactivated]]
        handler2_calls = [call for call in calls if call[0][1] in [handler2.on_user_registered, handler2.on_user_logged_in, handler2.on_user_deactivated]]
        
        assert len(handler1_calls) == 3
        assert len(handler2_calls) == 3


@pytest.mark.unit
class TestEventHandlersIntegration:
    """Tests de integración para event handlers"""
    
    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_all_event_handlers_work(self, mock_print):
        """Test: Todos los event handlers funcionan correctamente"""
        handler = UserEventHandler()
        
        # Crear eventos
        registered_event = UserRegisteredEvent("123", "testuser", "test@example.com")
        logged_in_event = UserLoggedInEvent("123", "testuser")
        deactivated_event = UserDeactivatedEvent("123")
        
        # Procesar todos los eventos
        await handler.on_user_registered(registered_event)
        await handler.on_user_logged_in(logged_in_event)
        await handler.on_user_deactivated(deactivated_event)
        
        # Verificar que se imprimieron todos los mensajes
        assert mock_print.call_count == 3
        
        # Verificar los mensajes específicos
        calls = mock_print.call_args_list
        messages = [call[0][0] for call in calls]
        
        assert "📧 [EVENT] Usuario registrado: testuser (test@example.com)" in messages
        assert "🔐 [EVENT] Usuario logueado: testuser" in messages
        assert "❌ [EVENT] Usuario desactivado: 123" in messages
    
    def test_event_handler_is_callable(self):
        """Test: Los métodos del event handler son callable"""
        handler = UserEventHandler()
        
        assert callable(handler.on_user_registered)
        assert callable(handler.on_user_logged_in)
        assert callable(handler.on_user_deactivated)
    
    def test_setup_event_handlers_is_callable(self):
        """Test: setup_event_handlers es callable"""
        assert callable(setup_event_handlers)
