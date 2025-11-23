"""
Tests adicionales para Product Handlers para aumentar cobertura
"""
import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from product.application.handlers import (
    AddStockCommandHandler,
    RemoveStockCommandHandler,
    DeactivateProductCommandHandler
)
from product.application.commands import (
    AddStockCommand,
    RemoveStockCommand,
    DeactivateProductCommand
)


@pytest.mark.unit
class TestAddStockCommandHandler:
    """Tests para AddStockCommandHandler"""
    
    @pytest.mark.asyncio
    async def test_add_stock_success(self):
        """Test agregar stock exitoso"""
        from product.domain.entities import Product
        
        mock_repo = Mock()
        mock_product = Mock(spec=Product)
        mock_product.add_stock = Mock()
        mock_product.get_domain_events = Mock(return_value=[])
        mock_product.clear_domain_events = Mock()
        
        mock_repo.find_by_id = AsyncMock(return_value=mock_product)
        mock_repo.save = AsyncMock(return_value=mock_product)
        
        handler = AddStockCommandHandler(mock_repo)
        
        command = AddStockCommand(
            product_id=str(uuid4()),
            amount=10
        )
        
        result = await handler.handle(command)
        
        assert result is not None
        mock_product.add_stock.assert_called_once_with(10)
        mock_repo.save.assert_called_once()


@pytest.mark.unit
class TestRemoveStockCommandHandler:
    """Tests para RemoveStockCommandHandler"""
    
    @pytest.mark.asyncio
    async def test_remove_stock_success(self):
        """Test remover stock exitoso"""
        from product.domain.entities import Product
        
        mock_repo = Mock()
        mock_product = Mock(spec=Product)
        mock_product.remove_stock = Mock()
        mock_product.get_domain_events = Mock(return_value=[])
        mock_product.clear_domain_events = Mock()
        
        mock_repo.find_by_id = AsyncMock(return_value=mock_product)
        mock_repo.save = AsyncMock(return_value=mock_product)
        
        handler = RemoveStockCommandHandler(mock_repo)
        
        command = RemoveStockCommand(
            product_id=str(uuid4()),
            amount=5
        )
        
        result = await handler.handle(command)
        
        assert result is not None
        mock_product.remove_stock.assert_called_once_with(5)
        mock_repo.save.assert_called_once()


@pytest.mark.unit
class TestDeactivateProductCommandHandler:
    """Tests para DeactivateProductCommandHandler"""
    
    @pytest.mark.asyncio
    async def test_deactivate_product_success(self):
        """Test desactivar producto exitoso"""
        from product.domain.entities import Product
        
        mock_repo = Mock()
        mock_product = Mock(spec=Product)
        mock_product.deactivate = Mock()
        mock_product.get_domain_events = Mock(return_value=[])
        mock_product.clear_domain_events = Mock()
        
        mock_repo.find_by_id = AsyncMock(return_value=mock_product)
        mock_repo.save = AsyncMock(return_value=mock_product)
        
        handler = DeactivateProductCommandHandler(mock_repo)
        
        command = DeactivateProductCommand(
            product_id=str(uuid4())
        )
        
        result = await handler.handle(command)
        
        assert result is not None
        mock_product.deactivate.assert_called_once()
        mock_repo.save.assert_called_once()

