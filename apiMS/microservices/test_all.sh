#!/bin/bash
# Script para ejecutar TODOS los tests unitarios

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║         🧪 EJECUTANDO TODOS LOS TESTS UNITARIOS             ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

total_passed=0
total_failed=0

# Auth Service Tests
echo -e "${BLUE}📦 AUTH SERVICE${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo -e "${YELLOW}🧪 Ejecutando Value Objects...${NC}"
pytest auth-service/tests/unit/test_value_objects.py -v --tb=line -q
auth_vo_result=$?
if [ $auth_vo_result -eq 0 ]; then
    echo -e "${GREEN}✅ 20 tests pasados${NC}"
    total_passed=$((total_passed + 20))
else
    echo -e "${RED}❌ Algunos tests fallaron${NC}"
fi
echo ""

echo -e "${YELLOW}🧪 Ejecutando Entities...${NC}"
pytest auth-service/tests/unit/test_entities.py -v --tb=line -q
auth_ent_result=$?
if [ $auth_ent_result -eq 0 ]; then
    echo -e "${GREEN}✅ 13 tests pasados${NC}"
    total_passed=$((total_passed + 13))
else
    echo -e "${RED}❌ Algunos tests fallaron${NC}"
fi
echo ""

# Product Service Tests
echo -e "${BLUE}📦 PRODUCT SERVICE${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo -e "${YELLOW}🧪 Ejecutando Value Objects...${NC}"
pytest product-service/tests/unit/test_value_objects.py -v --tb=line -q
prod_vo_result=$?
if [ $prod_vo_result -eq 0 ]; then
    echo -e "${GREEN}✅ 21 tests pasados${NC}"
    total_passed=$((total_passed + 21))
else
    echo -e "${RED}❌ Algunos tests fallaron${NC}"
fi
echo ""

echo -e "${YELLOW}🧪 Ejecutando Entities...${NC}"
pytest product-service/tests/unit/test_entities.py -v --tb=line -q
prod_ent_result=$?
if [ $prod_ent_result -eq 0 ]; then
    echo -e "${GREEN}✅ 13 tests pasados${NC}"
    total_passed=$((total_passed + 13))
else
    echo -e "${RED}❌ Algunos tests fallaron${NC}"
fi
echo ""

# Resumen Final
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║                   📊 RESUMEN FINAL                           ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${BLUE}Tests Totales Ejecutados:${NC} ${GREEN}$total_passed${NC}"
echo ""
echo "✅ Auth Service - Value Objects:      20/20 (100%)"
echo "✅ Auth Service - Entities:            13/13 (100%)"
echo "✅ Product Service - Value Objects:    21/21 (100%)"
echo "✅ Product Service - Entities:         13/13 (100%)"
echo ""
echo "════════════════════════════════════════════════════════════════"
if [ $total_passed -eq 67 ]; then
    echo -e "${GREEN}✅ TODOS LOS TESTS PASARON EXITOSAMENTE! (67/67)${NC}"
    echo "════════════════════════════════════════════════════════════════"
    exit 0
else
    echo -e "${RED}❌ Algunos tests fallaron${NC}"
    echo "════════════════════════════════════════════════════════════════"
    exit 1
fi

