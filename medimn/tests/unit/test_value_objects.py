"""
Tests unitarios para Value Objects
"""
import pytest
from shared.domain.value_objects import EntityId, Email, Money
from auth.domain.value_objects import Username, HashedPassword, FullName, PhoneNumber, UserRole, Address, InstitutionName
from product.domain.value_objects import ProductName, ProductDescription, Stock, Lot, Warehouse, Supplier, Category, VendorId


@pytest.mark.unit
class TestEntityId:
    """Tests para EntityId"""
    
    def test_create_entity_id(self):
        """Test crear EntityId"""
        entity_id = EntityId("test-id-123")
        assert str(entity_id) == "test-id-123"
    
    def test_entity_id_equality(self):
        """Test igualdad de EntityId"""
        id1 = EntityId("test-id")
        id2 = EntityId("test-id")
        id3 = EntityId("different-id")
        
        assert id1 == id2
        assert id1 != id3


@pytest.mark.unit
class TestEmail:
    """Tests para Email"""
    
    def test_create_valid_email(self):
        """Test crear email válido"""
        email = Email("test@example.com")
        assert str(email) == "test@example.com"
    
    def test_create_invalid_email(self):
        """Test crear email inválido"""
        with pytest.raises(ValueError):
            Email("invalid-email")


@pytest.mark.unit
class TestMoney:
    """Tests para Money"""
    
    def test_create_money(self):
        """Test crear Money"""
        money = Money(100.50)
        assert money.amount == 100.50
        assert money.currency == "USD"
    
    def test_money_operations(self):
        """Test operaciones con Money"""
        money1 = Money(100.0)
        money2 = Money(50.0)
        
        result_add = money1 + money2
        assert result_add.amount == 150.0
        
        result_sub = money1 - money2
        assert result_sub.amount == 50.0
    
    def test_money_negative(self):
        """Test crear Money negativo"""
        with pytest.raises(ValueError, match="no puede ser negativo"):
            Money(-10.0)
    
    def test_money_different_currencies(self):
        """Test operaciones con monedas diferentes"""
        money1 = Money(100.0, "USD")
        money2 = Money(50.0, "EUR")
        
        with pytest.raises(ValueError, match="monedas diferentes"):
            money1 + money2


@pytest.mark.unit
class TestUsername:
    """Tests para Username"""
    
    def test_create_username(self):
        """Test crear Username"""
        username = Username("testuser")
        assert str(username) == "testuser"
    
    def test_username_min_length(self):
        """Test validar longitud mínima de username"""
        with pytest.raises(ValueError):
            Username("ab")  # Muy corto


@pytest.mark.unit
class TestProductName:
    """Tests para ProductName"""
    
    def test_create_product_name(self):
        """Test crear ProductName"""
        name = ProductName("Test Product")
        assert str(name) == "Test Product"
    
    def test_product_name_empty(self):
        """Test crear ProductName vacío"""
        with pytest.raises(ValueError):
            ProductName("")


@pytest.mark.unit
class TestStock:
    """Tests para Stock"""
    
    def test_create_stock(self):
        """Test crear Stock"""
        stock = Stock(100)
        assert int(stock) == 100
    
    def test_stock_negative(self):
        """Test crear Stock negativo"""
        with pytest.raises(ValueError):
            Stock(-1)

