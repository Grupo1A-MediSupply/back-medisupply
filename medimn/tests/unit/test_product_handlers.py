"""
Tests unitarios para Product Handlers
"""
import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from product.application.handlers import (
    CreateProductCommandHandler,
    UpdateProductCommandHandler,
    GetProductByIdQueryHandler,
    GetAllProductsQueryHandler
)
from product.application.commands import (
    CreateProductCommand,
    UpdateProductCommand
)
from product.application.queries import (
    GetProductByIdQuery,
    GetAllProductsQuery
)
from shared.domain.value_objects import EntityId, Money


@pytest.mark.unit
class TestCreateProductCommandHandler:
    """Tests para CreateProductCommandHandler"""
    
    @pytest.mark.asyncio
    async def test_create_product_success(self):
        """Test crear producto exitoso"""
        from product.domain.entities import Product
        
        mock_repo = Mock()
        mock_product = Mock(spec=Product)
        mock_product.get_domain_events = Mock(return_value=[])
        mock_product.clear_domain_events = Mock()
        mock_repo.save = AsyncMock(return_value=mock_product)
        
        handler = CreateProductCommandHandler(mock_repo)
        
        command = CreateProductCommand(
            name="Test Product",
            price=100.0,
            description="Test Description",
            stock=50,
            is_active=True
        )
        
        result = await handler.handle(command)
        
        assert result is not None
        mock_repo.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_product_with_batches(self):
        """Test crear producto con batches"""
        from product.domain.entities import Product
        from product.application.commands import BatchData
        from datetime import datetime
        
        mock_repo = Mock()
        mock_product = Mock(spec=Product)
        mock_product.get_domain_events = Mock(return_value=[])
        mock_product.clear_domain_events = Mock()
        mock_repo.save = AsyncMock(return_value=mock_product)
        
        handler = CreateProductCommandHandler(mock_repo)
        
        command = CreateProductCommand(
            name="Test Product",
            price=100.0,
            stock=50,
            batches=[
                BatchData(
                    batch="BATCH001",
                    quantity=10,
                    expiry=datetime(2025, 12, 31),
                    location="Warehouse A"
                )
            ],
            is_active=True
        )
        
        result = await handler.handle(command)
        
        assert result is not None
        mock_repo.save.assert_called_once()


@pytest.mark.unit
class TestUpdateProductCommandHandler:
    """Tests para UpdateProductCommandHandler"""
    
    @pytest.mark.asyncio
    async def test_update_product_success(self):
        """Test actualizar producto exitoso"""
        from product.domain.entities import Product
        from product.domain.value_objects import ProductName, ProductDescription, Stock
        
        mock_repo = Mock()
        mock_product = Mock(spec=Product)
        mock_product.update = Mock()
        mock_product.get_domain_events = Mock(return_value=[])
        mock_product.clear_domain_events = Mock()
        
        mock_repo.find_by_id = AsyncMock(return_value=mock_product)
        mock_repo.save = AsyncMock(return_value=mock_product)
        
        handler = UpdateProductCommandHandler(mock_repo)
        
        command = UpdateProductCommand(
            product_id=str(uuid4()),
            name="Updated Product",
            price=150.0,
            description="Updated Description"
        )
        
        result = await handler.handle(command)
        
        assert result is not None
        mock_repo.find_by_id.assert_called_once()
        mock_repo.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_product_not_found(self):
        """Test actualizar producto no encontrado"""
        mock_repo = Mock()
        mock_repo.find_by_id = AsyncMock(return_value=None)
        
        handler = UpdateProductCommandHandler(mock_repo)
        
        command = UpdateProductCommand(
            product_id=str(uuid4()),
            name="Updated Product"
        )
        
        with pytest.raises(ValueError, match="Producto no encontrado"):
            await handler.handle(command)


@pytest.mark.unit
class TestGetProductByIdQueryHandler:
    """Tests para GetProductByIdQueryHandler"""
    
    @pytest.mark.asyncio
    async def test_get_product_by_id_success(self):
        """Test obtener producto por ID exitoso"""
        from product.domain.entities import Product
        
        mock_repo = Mock()
        mock_product = Mock(spec=Product)
        mock_repo.find_by_id = AsyncMock(return_value=mock_product)
        
        handler = GetProductByIdQueryHandler(mock_repo)
        
        query = GetProductByIdQuery(product_id=str(uuid4()))
        
        result = await handler.handle(query)
        
        assert result == mock_product
        mock_repo.find_by_id.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_product_by_id_not_found(self):
        """Test obtener producto por ID no encontrado"""
        mock_repo = Mock()
        mock_repo.find_by_id = AsyncMock(return_value=None)
        
        handler = GetProductByIdQueryHandler(mock_repo)
        
        query = GetProductByIdQuery(product_id=str(uuid4()))
        
        result = await handler.handle(query)
        
        assert result is None


@pytest.mark.unit
class TestGetAllProductsQueryHandler:
    """Tests para GetAllProductsQueryHandler"""
    
    @pytest.mark.asyncio
    async def test_get_all_products_success(self):
        """Test obtener todos los productos"""
        from product.domain.entities import Product
        
        mock_repo = Mock()
        mock_products = [Mock(spec=Product), Mock(spec=Product)]
        mock_repo.find_all = AsyncMock(return_value=mock_products)
        
        handler = GetAllProductsQueryHandler(mock_repo)
        
        query = GetAllProductsQuery()
        
        result = await handler.handle(query)
        
        assert result == mock_products
        assert len(result) == 2
        mock_repo.find_all.assert_called_once()

