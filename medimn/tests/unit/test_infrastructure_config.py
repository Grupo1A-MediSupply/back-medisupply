"""
Tests unitarios para Infrastructure Config
"""
import pytest
import os
from infrastructure.config import get_settings, MonolithSettings


@pytest.mark.unit
class TestMonolithSettings:
    """Tests para MonolithSettings"""
    
    def test_default_settings(self):
        """Test configuración por defecto"""
        settings = MonolithSettings()
        
        assert settings.service_name == "medisupply-monolith"
        assert settings.service_port == 8000
        assert settings.environment == "development"
        assert settings.debug is True
    
    def test_database_url_default(self):
        """Test URL de base de datos por defecto"""
        settings = MonolithSettings()
        
        assert "sqlite" in settings.database_url.lower()
    
    def test_secret_key_default(self):
        """Test secret key por defecto"""
        settings = MonolithSettings()
        
        assert settings.secret_key is not None
        assert len(settings.secret_key) > 0
    
    def test_allowed_origins_default(self):
        """Test allowed origins por defecto"""
        settings = MonolithSettings()
        
        assert isinstance(settings.allowed_origins, list)
        assert len(settings.allowed_origins) > 0
    
    def test_get_settings_singleton(self):
        """Test que get_settings retorna singleton"""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2

