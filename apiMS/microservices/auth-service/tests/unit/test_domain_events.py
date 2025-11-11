"""
Tests unitarios para eventos de dominio del Auth Service
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

# Agregar paths
auth_service_path = str(Path(__file__).parent.parent.parent)
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if auth_service_path not in sys.path:
    sys.path.insert(0, auth_service_path)
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from domain.events import UserRegisteredEvent, UserLoggedInEvent, UserDeactivatedEvent, TokenRefreshedEvent


@pytest.mark.unit
class TestUserRegisteredEvent:
    """Tests para el evento UserRegisteredEvent"""
    
    def test_crear_evento_registro_usuario(self):
        """Test: Crear evento de registro de usuario"""
        event = UserRegisteredEvent(
            user_id="123",
            username="testuser",
            email="test@example.com"
        )
        
        assert event.user_id == "123"
        assert event.username == "testuser"
        assert event.email == "test@example.com"
        assert event.aggregate_id == "123"
        assert isinstance(event.occurred_at, datetime)
    
    def test_event_data_registro_usuario(self):
        """Test: Datos del evento de registro"""
        event = UserRegisteredEvent(
            user_id="123",
            username="testuser",
            email="test@example.com"
        )
        
        event_data = event._event_data()
        expected_data = {
            "user_id": "123",
            "username": "testuser",
            "email": "test@example.com"
        }
        
        assert event_data == expected_data


@pytest.mark.unit
class TestUserLoggedInEvent:
    """Tests para el evento UserLoggedInEvent"""
    
    def test_crear_evento_login_usuario(self):
        """Test: Crear evento de login de usuario"""
        event = UserLoggedInEvent(
            user_id="123",
            username="testuser"
        )
        
        assert event.user_id == "123"
        assert event.username == "testuser"
        assert event.aggregate_id == "123"
        assert isinstance(event.occurred_at, datetime)
    
    def test_event_data_login_usuario(self):
        """Test: Datos del evento de login"""
        event = UserLoggedInEvent(
            user_id="123",
            username="testuser"
        )
        
        event_data = event._event_data()
        expected_data = {
            "user_id": "123",
            "username": "testuser"
        }
        
        assert event_data == expected_data


@pytest.mark.unit
class TestUserDeactivatedEvent:
    """Tests para el evento UserDeactivatedEvent"""
    
    def test_crear_evento_desactivacion_usuario(self):
        """Test: Crear evento de desactivación de usuario"""
        event = UserDeactivatedEvent(user_id="123")
        
        assert event.user_id == "123"
        assert event.aggregate_id == "123"
        assert isinstance(event.occurred_at, datetime)
    
    def test_event_data_desactivacion_usuario(self):
        """Test: Datos del evento de desactivación"""
        event = UserDeactivatedEvent(user_id="123")
        
        event_data = event._event_data()
        expected_data = {
            "user_id": "123"
        }
        
        assert event_data == expected_data


@pytest.mark.unit
class TestTokenRefreshedEvent:
    """Tests para el evento TokenRefreshedEvent"""
    
    def test_crear_evento_refresh_token(self):
        """Test: Crear evento de refresh token"""
        event = TokenRefreshedEvent(user_id="123")
        
        assert event.user_id == "123"
        assert event.aggregate_id == "123"
        assert isinstance(event.occurred_at, datetime)
    
    def test_event_data_refresh_token(self):
        """Test: Datos del evento de refresh token"""
        event = TokenRefreshedEvent(user_id="123")
        
        event_data = event._event_data()
        expected_data = {
            "user_id": "123"
        }
        
        assert event_data == expected_data


@pytest.mark.unit
class TestDomainEventsIntegration:
    """Tests de integración para eventos de dominio"""
    
    def test_eventos_herencia_domain_event(self):
        """Test: Todos los eventos heredan de DomainEvent"""
        from shared.domain.events import DomainEvent
        
        events = [
            UserRegisteredEvent("123", "test", "test@example.com"),
            UserLoggedInEvent("123", "test"),
            UserDeactivatedEvent("123"),
            TokenRefreshedEvent("123")
        ]
        
        for event in events:
            assert isinstance(event, DomainEvent)
    
    def test_eventos_tienen_timestamp(self):
        """Test: Todos los eventos tienen timestamp"""
        events = [
            UserRegisteredEvent("123", "test", "test@example.com"),
            UserLoggedInEvent("123", "test"),
            UserDeactivatedEvent("123"),
            TokenRefreshedEvent("123")
        ]
        
        for event in events:
            assert hasattr(event, 'occurred_at')
            assert isinstance(event.occurred_at, datetime)
    
    def test_eventos_tienen_aggregate_id(self):
        """Test: Todos los eventos tienen aggregate_id"""
        events = [
            UserRegisteredEvent("123", "test", "test@example.com"),
            UserLoggedInEvent("123", "test"),
            UserDeactivatedEvent("123"),
            TokenRefreshedEvent("123")
        ]
        
        for event in events:
            assert hasattr(event, 'aggregate_id')
            assert event.aggregate_id == "123"
