"""
Tests unitarios para Product Entities
"""
import pytest
from uuid import uuid4
from shared.domain.value_objects import EntityId, Money
from product.domain.value_objects import ProductName, ProductDescription, Stock, Lot, Warehouse, Supplier, Category, VendorId
from product.domain.entities import Product, Batch


@pytest.mark.unit
class TestProductEntity:
    """Tests para Product Entity"""
    
    def test_create_product(self):
        """Test crear producto"""
        product_id = EntityId(str(uuid4()))
        name = ProductName("Test Product")
        price = Money(100.0)
        stock = Stock(50)
        
        product = Product.create(
            product_id=product_id,
            name=name,
            price=price,
            stock=stock,
            is_active=True
        )
        
        assert product is not None
        assert product.id == product_id
        assert product.name == name
        assert product.price == price
        assert product.stock == stock
        assert product.is_active is True
    
    def test_update_product_name(self):
        """Test actualizar nombre del producto"""
        product_id = EntityId(str(uuid4()))
        name = ProductName("Test Product")
        price = Money(100.0)
        stock = Stock(50)
        
        product = Product.create(
            product_id=product_id,
            name=name,
            price=price,
            stock=stock,
            is_active=True
        )
        
        new_name = ProductName("Updated Product")
        product.update_name(new_name)
        
        assert product.name == new_name
    
    def test_update_product_price(self):
        """Test actualizar precio del producto"""
        product_id = EntityId(str(uuid4()))
        name = ProductName("Test Product")
        price = Money(100.0)
        stock = Stock(50)
        
        product = Product.create(
            product_id=product_id,
            name=name,
            price=price,
            stock=stock,
            is_active=True
        )
        
        new_price = Money(150.0)
        product.update_price(new_price)
        
        assert product.price == new_price
    
    def test_add_stock(self):
        """Test agregar stock"""
        product_id = EntityId(str(uuid4()))
        name = ProductName("Test Product")
        price = Money(100.0)
        stock = Stock(50)
        
        product = Product.create(
            product_id=product_id,
            name=name,
            price=price,
            stock=stock,
            is_active=True
        )
        
        product.add_stock(25)  # add_stock recibe int, no Stock
        
        assert product.stock.quantity == 75
    
    def test_remove_stock(self):
        """Test remover stock"""
        product_id = EntityId(str(uuid4()))
        name = ProductName("Test Product")
        price = Money(100.0)
        stock = Stock(50)
        
        product = Product.create(
            product_id=product_id,
            name=name,
            price=price,
            stock=stock,
            is_active=True
        )
        
        product.remove_stock(20)  # remove_stock recibe int, no Stock
        
        assert product.stock.quantity == 30
    
    def test_deactivate_product(self):
        """Test desactivar producto"""
        product_id = EntityId(str(uuid4()))
        name = ProductName("Test Product")
        price = Money(100.0)
        stock = Stock(50)
        
        product = Product.create(
            product_id=product_id,
            name=name,
            price=price,
            stock=stock,
            is_active=True
        )
        
        product.deactivate()
        
        assert product.is_active is False


@pytest.mark.unit
class TestBatch:
    """Tests para Batch"""
    
    def test_create_batch(self):
        """Test crear batch"""
        batch = Batch(
            batch="BATCH001",
            quantity=10,
            expiry="2025-12-31",
            location="Warehouse A"
        )
        
        assert batch.batch == "BATCH001"
        assert batch.quantity == 10
        assert batch.expiry == "2025-12-31"
        assert batch.location == "Warehouse A"

