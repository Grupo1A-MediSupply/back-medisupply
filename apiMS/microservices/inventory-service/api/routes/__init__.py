"""
Rutas de la API de inventario
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import io
import csv

from ..infrastructure.database import get_db
from ..infrastructure.config import get_settings

router = APIRouter()
settings = get_settings()


# ========== Schemas ==========

class InventoryItemResponse(BaseModel):
    """Response para item de inventario"""
    id: str
    sku: str
    name: str
    stock: int
    min_stock: int
    max_stock: int
    location: str
    category: Optional[str] = None
    unit_price: Optional[float] = None
    is_active: bool


class InventoryUploadResponse(BaseModel):
    """Response para upload de inventario"""
    success: bool
    total_items: int
    imported: int
    errors: List[str] = []


# ========== Endpoints ==========

@router.get(
    "/inventory",
    response_model=List[InventoryItemResponse],
    summary="Listar inventario",
    description="Lista todos los items de inventario"
)
async def list_inventory(
    active_only: bool = True,
    low_stock_only: bool = False,
    category: Optional[str] = None
):
    """Listar items de inventario"""
    # TODO: Implementar lógica real con repositorio
    # Por ahora retorna mock data para cumplir contrato
    
    mock_items = [
        {
            "id": "INV-001",
            "sku": "SKU-001",
            "name": "Producto Test 1",
            "stock": 50,
            "min_stock": 10,
            "max_stock": 1000,
            "location": "Almacén Principal",
            "category": "Suministros Médicos",
            "unit_price": 100.0,
            "is_active": True
        },
        {
            "id": "INV-002",
            "sku": "SKU-002",
            "name": "Producto Test 2",
            "stock": 5,
            "min_stock": 10,
            "max_stock": 500,
            "location": "Almacén Principal",
            "category": "Equipamiento",
            "unit_price": 250.0,
            "is_active": True
        }
    ]
    
    # Filtrar por low_stock_only
    if low_stock_only:
        mock_items = [item for item in mock_items if item["stock"] <= item["min_stock"]]
    
    # Filtrar por category
    if category:
        mock_items = [item for item in mock_items if item.get("category") == category]
    
    # Filtrar por active_only
    if active_only:
        mock_items = [item for item in mock_items if item["is_active"]]
    
    return mock_items


@router.post(
    "/inventory/upload",
    response_model=InventoryUploadResponse,
    summary="Subir inventario",
    description="Sube un archivo CSV para importar items de inventario"
)
async def upload_inventory(
    file: UploadFile = File(...),
    validate_only: bool = False,
    update_existing: bool = False
):
    """Subir archivo CSV de inventario"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser CSV"
        )
    
    # Leer contenido del archivo
    content = await file.read()
    csv_data = io.StringIO(content.decode('utf-8'))
    reader = csv.DictReader(csv_data)
    
    items = list(reader)
    total_items = len(items)
    
    # TODO: Implementar lógica real de importación
    # Por ahora retorna mock response
    
    return InventoryUploadResponse(
        success=True,
        total_items=total_items,
        imported=total_items if not validate_only else 0,
        errors=[]
    )


@router.get(
    "/inventory/template",
    summary="Template de inventario",
    description="Descarga un template CSV para importar items de inventario"
)
async def get_inventory_template():
    """Descargar template CSV"""
    # Crear template CSV en memoria
    template_data = io.StringIO()
    writer = csv.writer(template_data)
    
    # Escribir headers
    writer.writerow([
        'sku',
        'name',
        'stock',
        'min_stock',
        'max_stock',
        'location',
        'supplier',
        'category',
        'unit_price'
    ])
    
    # Escribir fila de ejemplo
    writer.writerow([
        'SKU-001',
        'Producto de Ejemplo',
        '100',
        '10',
        '1000',
        'Almacén Principal',
        'Proveedor Ejemplo',
        'Suministros',
        '100.0'
    ])
    
    template_data.seek(0)
    
    # Retornar archivo
    return StreamingResponse(
        iter([template_data.getvalue()]),
        media_type='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename="inventory_template.csv"'
        }
    )

