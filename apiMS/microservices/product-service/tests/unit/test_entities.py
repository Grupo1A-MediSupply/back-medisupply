"""
Tests unitarios para entidades del dominio de Products
"""
import pytest
import sys
from pathlib import Path

# Agregar paths
product_service_path = str(Path(__file__).parent.parent.parent)
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if product_service_path not in sys.path:
    sys.path.insert(0, product_service_path)
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.value_objects import EntityId, Money
from domain.value_objects import ProductName, ProductDescription, Stock
from domain.entities import Product
from domain.events import (
    ProductCreatedEvent,
    ProductUpdatedEvent,
    ProductDeactivatedEvent,
    StockUpdatedEvent,
    LowStockEvent
)


@pytest.mark.unit
class TestProductEntity:
    """Tests para la entidad Product"""
    
    def test_crear_producto(self):
        """Test: Producto se crea correctamente"""
        product = Product(
            product_id=EntityId("prod-123"),
            name=ProductName("Laptop"),
            price=Money(999.99),
            description=ProductDescription("Laptop de alto rendimiento"),
            stock=Stock(10),
            is_active=True
        )
        
        assert str(product.id) == "prod-123"
        assert str(product.name) == "Laptop"
        assert product.price.amount == 999.99
        assert product.stock.quantity == 10
        assert product.is_active is True
    
    def test_create_factory_method(self):
        """Test: Factory method create genera producto y evento"""
        product = Product.create(
            product_id=EntityId("prod-123"),
            name=ProductName("Laptop"),
            price=Money(999.99),
            description=ProductDescription("Laptop de alto rendimiento"),
            stock=Stock(10)
        )
        
        assert str(product.id) == "prod-123"
        
        # Verificar evento
        events = product.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], ProductCreatedEvent)
        assert events[0].product_id == "prod-123"
        assert events[0].name == "Laptop"
        assert events[0].price == 999.99
    
    def test_update_name(self):
        """Test: Actualizar nombre registra evento"""
        product = Product(
            product_id=EntityId("prod-123"),
            name=ProductName("Laptop"),
            price=Money(999.99),
            stock=Stock(10)
        )
        
        product.update_name(ProductName("Laptop Dell"))
        
        assert str(product.name) == "Laptop Dell"
        events = product.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], ProductUpdatedEvent)
    
    def test_update_price(self):
        """Test: Actualizar precio registra evento"""
        product = Product(
            product_id=EntityId("prod-123"),
            name=ProductName("Laptop"),
            price=Money(999.99),
            stock=Stock(10)
        )
        
        product.update_price(Money(899.99))
        
        assert product.price.amount == 899.99
        events = product.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], ProductUpdatedEvent)
    
    def test_update_price_diferente_moneda_lanza_error(self):
        """Test: Cambiar moneda del producto lanza excepción"""
        product = Product(
            product_id=EntityId("prod-123"),
            name=ProductName("Laptop"),
            price=Money(999.99, "USD"),
            stock=Stock(10)
        )
        
        with pytest.raises(ValueError, match="moneda"):
            product.update_price(Money(899.99, "EUR"))
    
    def test_add_stock(self):
        """Test: Agregar stock registra evento"""
        product = Product(
            product_id=EntityId("prod-123"),
            name=ProductName("Laptop"),
            price=Money(999.99),
            stock=Stock(10)
        )
        
        product.add_stock(5)
        
        assert product.stock.quantity == 15
        events = product.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], StockUpdatedEvent)
        assert events[0].old_stock == 10
        assert events[0].new_stock == 15
    
    def test_remove_stock(self):
        """Test: Remover stock registra evento"""
        product = Product(
            product_id=EntityId("prod-123"),
            name=ProductName("Laptop"),
            price=Money(999.99),
            stock=Stock(20)  # Stock mayor al threshold para no generar LowStock
        )
        
        product.remove_stock(3)
        
        assert product.stock.quantity == 17
        events = product.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], StockUpdatedEvent)
    
    def test_remove_stock_insuficiente_lanza_error(self):
        """Test: Remover más stock del disponible lanza excepción"""
        product = Product(
            product_id=EntityId("prod-123"),
            name=ProductName("Laptop"),
            price=Money(999.99),
            stock=Stock(10)
        )
        
        with pytest.raises(ValueError, match="insuficiente"):
            product.remove_stock(15)
    
    def test_remove_stock_genera_evento_low_stock(self):
        """Test: Remover stock hasta threshold genera evento LowStock"""
        product = Product(
            product_id=EntityId("prod-123"),
            name=ProductName("Laptop"),
            price=Money(999.99),
            stock=Stock(15)
        )
        
        product.remove_stock(10)  # Queda en 5, debajo del threshold (10)
        
        events = product.get_domain_events()
        assert len(events) == 2
        assert isinstance(events[0], StockUpdatedEvent)
        assert isinstance(events[1], LowStockEvent)
        assert events[1].current_stock == 5
        assert events[1].threshold == 10
    
    def test_deactivate_product(self):
        """Test: Desactivar producto cambia estado y registra evento"""
        product = Product(
            product_id=EntityId("prod-123"),
            name=ProductName("Laptop"),
            price=Money(999.99),
            stock=Stock(10),
            is_active=True
        )
        
        product.deactivate()
        
        assert product.is_active is False
        events = product.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], ProductDeactivatedEvent)
    
    def test_deactivate_producto_ya_inactivo_lanza_error(self):
        """Test: Desactivar producto ya inactivo lanza excepción"""
        product = Product(
            product_id=EntityId("prod-123"),
            name=ProductName("Laptop"),
            price=Money(999.99),
            stock=Stock(10),
            is_active=False
        )
        
        with pytest.raises(ValueError, match="ya está desactivado"):
            product.deactivate()
    
    def test_activate_product(self):
        """Test: Activar producto cambia estado"""
        product = Product(
            product_id=EntityId("prod-123"),
            name=ProductName("Laptop"),
            price=Money(999.99),
            stock=Stock(10),
            is_active=False
        )
        
        product.activate()
        
        assert product.is_active is True
    
    def test_activate_producto_ya_activo_lanza_error(self):
        """Test: Activar producto ya activo lanza excepción"""
        product = Product(
            product_id=EntityId("prod-123"),
            name=ProductName("Laptop"),
            price=Money(999.99),
            stock=Stock(10),
            is_active=True
        )
        
        with pytest.raises(ValueError, match="ya está activo"):
            product.activate()

