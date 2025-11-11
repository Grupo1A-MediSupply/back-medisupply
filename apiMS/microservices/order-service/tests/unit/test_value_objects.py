"""
Tests unitarios para value objects
"""
import pytest
from datetime import datetime
from ...domain.entities import OrderItem, ETA


def test_create_order_item():
    """Test crear OrderItem"""
    item = OrderItem(sku_id="SKU001", qty=2, price=10.0)
    
    assert item.sku_id == "SKU001"
    assert item.qty == 2
    assert item.price == 10.0
    assert item.subtotal == 20.0


def test_create_order_item_calculates_subtotal():
    """Test que OrderItem calcula subtotal automáticamente"""
    item = OrderItem(sku_id="SKU001", qty=5, price=15.0)
    
    assert item.subtotal == 75.0


def test_create_order_item_with_zero_qty_raises_error():
    """Test que crear OrderItem con qty=0 lanza error"""
    with pytest.raises(ValueError, match="mayor a 0"):
        OrderItem(sku_id="SKU001", qty=0, price=10.0)


def test_create_order_item_with_negative_qty_raises_error():
    """Test que crear OrderItem con qty negativa lanza error"""
    with pytest.raises(ValueError, match="mayor a 0"):
        OrderItem(sku_id="SKU001", qty=-1, price=10.0)


def test_create_order_item_with_negative_price_raises_error():
    """Test que crear OrderItem con precio negativo lanza error"""
    with pytest.raises(ValueError, match="no puede ser negativo"):
        OrderItem(sku_id="SKU001", qty=1, price=-10.0)


def test_create_order_item_with_empty_sku_raises_error():
    """Test que crear OrderItem con SKU vacío lanza error"""
    with pytest.raises(ValueError, match="SKU ID es requerido"):
        OrderItem(sku_id="", qty=1, price=10.0)
    
    with pytest.raises(ValueError, match="SKU ID es requerido"):
        OrderItem(sku_id="   ", qty=1, price=10.0)


def test_order_item_to_dict():
    """Test conversión de OrderItem a diccionario"""
    item = OrderItem(sku_id="SKU001", qty=2, price=10.0)
    
    item_dict = item.to_dict()
    
    assert item_dict == {
        "skuId": "SKU001",
        "qty": 2,
        "price": 10.0
    }


def test_create_eta():
    """Test crear ETA"""
    date = datetime(2024, 12, 31, 18, 0, 0)
    eta = ETA(date=date, window_minutes=60)
    
    assert eta.date == date
    assert eta.window_minutes == 60


def test_create_eta_with_negative_window_raises_error():
    """Test que crear ETA con ventana negativa lanza error"""
    date = datetime(2024, 12, 31, 18, 0, 0)
    
    with pytest.raises(ValueError, match="no puede ser negativa"):
        ETA(date=date, window_minutes=-1)


def test_eta_to_dict():
    """Test conversión de ETA a diccionario"""
    date = datetime(2024, 12, 31, 18, 0, 0)
    eta = ETA(date=date, window_minutes=60)
    
    eta_dict = eta.to_dict()
    
    assert eta_dict["date"] == date.isoformat()
    assert eta_dict["windowMinutes"] == 60


def test_order_item_with_different_skus():
    """Test crear múltiples OrderItems con diferentes SKUs"""
    items = [
        OrderItem(sku_id="SKU001", qty=2, price=10.0),
        OrderItem(sku_id="SKU002", qty=3, price=15.0),
        OrderItem(sku_id="SKU003", qty=1, price=20.0)
    ]
    
    assert len(items) == 3
    assert items[0].subtotal == 20.0
    assert items[1].subtotal == 45.0
    assert items[2].subtotal == 20.0


def test_order_item_with_decimal_prices():
    """Test OrderItem con precios decimales"""
    item = OrderItem(sku_id="SKU001", qty=3, price=9.99)
    
    # El subtotal debe manejar decimales
    assert abs(item.subtotal - 29.97) < 0.001


def test_order_item_with_large_qty():
    """Test OrderItem con cantidad grande"""
    item = OrderItem(sku_id="SKU001", qty=1000, price=1.0)
    
    assert item.subtotal == 1000.0

