"""
Tests unitarios para las rutas de API en notifications-service
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Los paths están configurados en conftest.py
from api.routes import router


def create_app():
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


def test_get_notifications_returns_list_and_filters_by_is_read():
    app = create_app()
    client = TestClient(app)

    # Sin filtros
    r = client.get("/api/v1/notifications")
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)
    assert len(items) >= 3

    # Filtrando por is_read=true
    r2 = client.get("/api/v1/notifications", params={"is_read": True})
    assert r2.status_code == 200
    only_read = r2.json()
    assert all(item["is_read"] is True for item in only_read)

    # Filtrando por is_read=false
    r3 = client.get("/api/v1/notifications", params={"is_read": False})
    assert r3.status_code == 200
    only_unread = r3.json()
    assert all(item["is_read"] is False for item in only_unread)


def test_get_notifications_filters_by_type_and_limit():
    app = create_app()
    client = TestClient(app)

    r = client.get("/api/v1/notifications", params={"notification_type": "order", "limit": 1})
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["type"] == "order"


def test_mark_notification_as_read_happy_path_and_not_found():
    app = create_app()
    client = TestClient(app)

    # Happy path
    r = client.put("/api/v1/notifications/notif_001/read")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert "marcada como leída" in body["message"]

    # Not found (notification_id vacío)
    r2 = client.put("/api/v1/notifications//read")
    assert r2.status_code == 404


