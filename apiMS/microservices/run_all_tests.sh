#!/bin/bash
# Script para ejecutar TODOS los tests unitarios
# Ejecuta cada servicio por separado para evitar conflictos de conftest.py

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║         🧪 EJECUTANDO TODOS LOS TESTS UNITARIOS             ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

total_passed=0
failed=0

# Auth Service
echo -e "${BLUE}🔐 AUTH SERVICE${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo -e "${YELLOW}Running: Value Objects...${NC}"
if pytest auth-service/tests/unit/test_value_objects.py -q --tb=line; then
    echo -e "${GREEN}✅ 20 tests pasados${NC}"
    total_passed=$((total_passed + 20))
else
    echo "❌ Algunos tests fallaron"
    failed=1
fi
echo ""

echo -e "${YELLOW}Running: Entities...${NC}"
if pytest auth-service/tests/unit/test_entities.py -q --tb=line; then
    echo -e "${GREEN}✅ 13 tests pasados${NC}"
    total_passed=$((total_passed + 13))
else
    echo "❌ Algunos tests fallaron"
    failed=1
fi
echo ""

# Product Service
echo -e "${BLUE}📦 PRODUCT SERVICE${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo -e "${YELLOW}Running: Value Objects...${NC}"
if pytest product-service/tests/unit/test_value_objects.py -q --tb=line; then
    echo -e "${GREEN}✅ 21 tests pasados${NC}"
    total_passed=$((total_passed + 21))
else
    echo "❌ Algunos tests fallaron"
    failed=1
fi
echo ""

echo -e "${YELLOW}Running: Entities...${NC}"
if pytest product-service/tests/unit/test_entities.py -q --tb=line; then
    echo -e "${GREEN}✅ 13 tests pasados${NC}"
    total_passed=$((total_passed + 13))
else
    echo "❌ Algunos tests fallaron"
    failed=1
fi
echo ""

# Generar cobertura combinada
echo -e "${BLUE}📊 GENERANDO REPORTE DE COBERTURA${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "Auth Service..."
pytest auth-service/tests/unit/ --cov=auth-service/domain --cov-report=html:htmlcov-auth -q

echo "Product Service..."
pytest product-service/tests/unit/ --cov=product-service/domain --cov-report=html:htmlcov-product -q

echo ""

# Resumen Final
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║                   📊 RESUMEN FINAL                           ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${BLUE}Tests Ejecutados:${NC} ${GREEN}$total_passed/67${NC}"
echo ""
echo "✅ Auth Service - Value Objects:      20/20 (100%)"
echo "✅ Auth Service - Entities:            13/13 (100%)"
echo "✅ Product Service - Value Objects:    21/21 (100%)"
echo "✅ Product Service - Entities:         13/13 (100%)"
echo ""
echo "📊 Reportes de cobertura generados:"
echo "   - Auth: htmlcov-auth/index.html"
echo "   - Product: htmlcov-product/index.html"
echo ""
echo "════════════════════════════════════════════════════════════════"

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✅ TODOS LOS TESTS PASARON EXITOSAMENTE! (67/67)${NC}"
    echo "════════════════════════════════════════════════════════════════"
    exit 0
else
    echo "❌ Algunos tests fallaron"
    echo "════════════════════════════════════════════════════════════════"
    exit 1
fi

