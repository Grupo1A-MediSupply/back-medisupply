"""
Tests unitarios para value objects
"""
import pytest
from datetime import datetime
from ...domain.entities import Stop, ETA, Position


def test_create_stop():
    """Test crear Stop"""
    stop = Stop(order_id="ORD001", priority=1)
    
    assert stop.order_id == "ORD001"
    assert stop.priority == 1
    assert stop.eta is None


def test_create_stop_with_eta():
    """Test crear Stop con ETA"""
    eta = ETA(
        date=datetime(2024, 12, 31, 18, 0, 0),
        window_minutes=60
    )
    
    stop = Stop(order_id="ORD001", priority=1, eta=eta)
    
    assert stop.order_id == "ORD001"
    assert stop.eta is not None
    assert stop.eta.window_minutes == 60


def test_create_stop_with_empty_order_id_raises_error():
    """Test que crear Stop con order_id vacío lanza error"""
    with pytest.raises(ValueError, match="Order ID es requerido"):
        Stop(order_id="", priority=1)


def test_create_stop_with_zero_priority_raises_error():
    """Test que crear Stop con prioridad 0 lanza error"""
    with pytest.raises(ValueError, match="mayor a 0"):
        Stop(order_id="ORD001", priority=0)


def test_stop_to_dict():
    """Test conversión de Stop a diccionario"""
    eta = ETA(
        date=datetime(2024, 12, 31, 18, 0, 0),
        window_minutes=60
    )
    
    stop = Stop(order_id="ORD001", priority=1, eta=eta)
    stop_dict = stop.to_dict()
    
    assert stop_dict["orderId"] == "ORD001"
    assert stop_dict["priority"] == 1
    assert "eta" in stop_dict


def test_stop_to_dict_without_eta():
    """Test conversión de Stop sin ETA a diccionario"""
    stop = Stop(order_id="ORD001", priority=2)
    stop_dict = stop.to_dict()
    
    assert stop_dict["orderId"] == "ORD001"
    assert stop_dict["priority"] == 2
    assert "eta" not in stop_dict


def test_create_position():
    """Test crear Position"""
    position = Position(
        lat=19.4326,
        lon=-99.1332,
        timestamp=datetime.now()
    )
    
    assert position.lat == 19.4326
    assert position.lon == -99.1332


def test_create_position_with_invalid_lat():
    """Test que crear Position con latitud inválida lanza error"""
    with pytest.raises(ValueError, match="Latitud"):
        Position(lat=91, lon=0, timestamp=datetime.now())


def test_create_position_with_invalid_lon():
    """Test que crear Position con longitud inválida lanza error"""
    with pytest.raises(ValueError, match="Longitud"):
        Position(lat=0, lon=-181, timestamp=datetime.now())


def test_position_to_dict():
    """Test conversión de Position a diccionario"""
    timestamp = datetime.now()
    position = Position(lat=19.4326, lon=-99.1332, timestamp=timestamp)
    
    position_dict = position.to_dict()
    
    assert position_dict["lat"] == 19.4326
    assert position_dict["lon"] == -99.1332


def test_create_eta():
    """Test crear ETA"""
    eta = ETA(
        date=datetime(2024, 12, 31, 18, 0, 0),
        window_minutes=60
    )
    
    assert eta.window_minutes == 60


def test_create_eta_with_negative_window():
    """Test que crear ETA con ventana negativa lanza error"""
    with pytest.raises(ValueError, match="no puede ser negativa"):
        ETA(
            date=datetime(2024, 12, 31, 18, 0, 0),
            window_minutes=-1
        )


def test_eta_to_dict():
    """Test conversión de ETA a diccionario"""
    eta = ETA(
        date=datetime(2024, 12, 31, 18, 0, 0),
        window_minutes=60
    )
    
    eta_dict = eta.to_dict()
    
    assert eta_dict["windowMinutes"] == 60
    assert "date" in eta_dict

