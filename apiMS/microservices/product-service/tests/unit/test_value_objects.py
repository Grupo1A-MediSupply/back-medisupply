"""
Tests unitarios para Value Objects del dominio de Products
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

from shared.domain.value_objects import Money
from domain.value_objects import ProductName, ProductDescription, Stock


@pytest.mark.unit
class TestProductName:
    """Tests para el Value Object ProductName"""
    
    def test_product_name_valido(self):
        """Test: ProductName válido se crea correctamente"""
        name = ProductName("Laptop Dell XPS")
        assert name.value == "Laptop Dell XPS"
        assert str(name) == "Laptop Dell XPS"
    
    def test_product_name_vacio(self):
        """Test: ProductName vacío lanza excepción"""
        with pytest.raises(ValueError, match="no puede estar vacío"):
            ProductName("")
    
    def test_product_name_muy_largo(self):
        """Test: ProductName mayor a 255 caracteres lanza excepción"""
        with pytest.raises(ValueError, match="no puede tener más de 255 caracteres"):
            ProductName("a" * 256)
    
    def test_product_name_es_inmutable(self):
        """Test: ProductName es inmutable"""
        name = ProductName("Laptop")
        with pytest.raises(AttributeError):
            name.value = "Otro nombre"


@pytest.mark.unit
class TestProductDescription:
    """Tests para el Value Object ProductDescription"""
    
    def test_product_description_valida(self):
        """Test: ProductDescription válida se crea correctamente"""
        desc = ProductDescription("Descripción del producto")
        assert desc.value == "Descripción del producto"
    
    def test_product_description_vacia(self):
        """Test: ProductDescription vacía es válida"""
        desc = ProductDescription("")
        assert str(desc) == ""
    
    def test_product_description_none(self):
        """Test: ProductDescription None es válida"""
        desc = ProductDescription(None)
        assert str(desc) == ""
    
    def test_product_description_muy_larga(self):
        """Test: ProductDescription mayor a 1000 caracteres lanza excepción"""
        with pytest.raises(ValueError, match="no puede tener más de 1000 caracteres"):
            ProductDescription("a" * 1001)


@pytest.mark.unit
class TestStock:
    """Tests para el Value Object Stock"""
    
    def test_stock_valido(self):
        """Test: Stock válido se crea correctamente"""
        stock = Stock(10)
        assert stock.quantity == 10
        assert int(stock) == 10
    
    def test_stock_negativo(self):
        """Test: Stock negativo lanza excepción"""
        with pytest.raises(ValueError, match="no puede ser negativo"):
            Stock(-1)
    
    def test_stock_cero_valido(self):
        """Test: Stock cero es válido"""
        stock = Stock(0)
        assert stock.quantity == 0
    
    def test_add_stock(self):
        """Test: Agregar stock suma correctamente"""
        stock = Stock(10)
        new_stock = stock.add(5)
        assert new_stock.quantity == 15
        assert stock.quantity == 10  # Original no cambia
    
    def test_add_stock_negativo_lanza_error(self):
        """Test: Agregar cantidad negativa lanza excepción"""
        stock = Stock(10)
        with pytest.raises(ValueError, match="cantidad negativa"):
            stock.add(-5)
    
    def test_remove_stock(self):
        """Test: Remover stock resta correctamente"""
        stock = Stock(10)
        new_stock = stock.remove(3)
        assert new_stock.quantity == 7
        assert stock.quantity == 10  # Original no cambia
    
    def test_remove_stock_insuficiente_lanza_error(self):
        """Test: Remover más stock del disponible lanza excepción"""
        stock = Stock(10)
        with pytest.raises(ValueError, match="insuficiente"):
            stock.remove(15)
    
    def test_is_available(self):
        """Test: is_available verifica disponibilidad"""
        stock = Stock(10)
        assert stock.is_available(5) is True
        assert stock.is_available(10) is True
        assert stock.is_available(11) is False


@pytest.mark.unit
class TestMoney:
    """Tests para el Value Object Money"""
    
    def test_money_valido(self):
        """Test: Money válido se crea correctamente"""
        money = Money(99.99)
        assert money.amount == 99.99
        assert money.currency == "USD"
        assert str(money) == "99.99 USD"
    
    def test_money_negativo_lanza_error(self):
        """Test: Money negativo lanza excepción"""
        with pytest.raises(ValueError, match="no puede ser negativo"):
            Money(-10.0)
    
    def test_money_suma(self):
        """Test: Sumar dinero funciona correctamente"""
        money1 = Money(10.0)
        money2 = Money(5.0)
        result = money1 + money2
        assert result.amount == 15.0
    
    def test_money_resta(self):
        """Test: Restar dinero funciona correctamente"""
        money1 = Money(10.0)
        money2 = Money(5.0)
        result = money1 - money2
        assert result.amount == 5.0
    
    def test_money_diferentes_monedas_lanza_error(self):
        """Test: Operar con diferentes monedas lanza excepción"""
        money_usd = Money(10.0, "USD")
        money_eur = Money(10.0, "EUR")
        
        with pytest.raises(ValueError, match="monedas diferentes"):
            money_usd + money_eur

