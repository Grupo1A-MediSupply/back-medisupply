"""
Tests unitarios para la configuración del servicio de notificaciones
"""
# Los paths están configurados en conftest.py
# Los imports se hacen dentro de las funciones para evitar problemas de importación


def test_settings_default_values(monkeypatch):
    # Los imports se hacen aquí para evitar problemas cuando pytest carga el módulo
    from infrastructure.config import get_settings, NotificationsServiceSettings
    
    # Asegurar que variables de entorno no interfieran
    for var in [
        "NOTIFICATIONS_SERVICE_PORT",
        "ENVIRONMENT",
        "DEBUG",
        "NOTIFICATIONS_DATABASE_URL",
        "ALLOWED_ORIGINS",
        "AUTH_SERVICE_URL",
    ]:
        monkeypatch.delenv(var, raising=False)

    # Forzar nueva instancia
    from importlib import reload
    import infrastructure.config as cfg
    reload(cfg)

    settings = cfg.get_settings()
    assert isinstance(settings, NotificationsServiceSettings)
    assert settings.service_name == "notifications-service"
    assert settings.service_port == 8007
    assert settings.environment == "development"
    assert settings.debug is True
    assert settings.database_url.startswith("sqlite:///./notifications_service.db")
    assert "http://localhost:3000" in settings.allowed_origins
    assert settings.auth_service_url.startswith("http://auth-service:")


def test_settings_env_override(monkeypatch):
    # Los imports se hacen aquí para evitar problemas cuando pytest carga el módulo
    from infrastructure.config import NotificationsServiceSettings
    
    monkeypatch.setenv("NOTIFICATIONS_SERVICE_PORT", "9000")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("NOTIFICATIONS_DATABASE_URL", "sqlite:///./test.db")
    monkeypatch.setenv("AUTH_SERVICE_URL", "http://custom-auth:1234")

    from importlib import reload
    import infrastructure.config as cfg
    reload(cfg)

    s = cfg.get_settings()
    assert s.service_port == 9000
    assert s.environment == "production"
    assert s.debug is False
    assert s.database_url.endswith("test.db")
    assert s.auth_service_url == "http://custom-auth:1234"


