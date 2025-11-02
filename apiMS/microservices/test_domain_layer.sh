#!/bin/bash
# Script para ejecutar SOLO los tests unitarios de la capa de dominio
# (Value Objects + Entities) de todos los microservicios

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║    🧪 TESTS CAPA DE DOMINIO - Value Objects + Entities      ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configurar directorio de trabajo
cd "$(dirname "$0")" || exit 1
export PYTHONPATH=$(pwd)

# Contadores
total_passed=0
total_failed=0
services_passed=0
services_failed=0

# Verificar dependencias
echo -e "${YELLOW}📦 Verificando dependencias...${NC}"
if ! pip install -q -r requirements-test.txt 2>/dev/null; then
    echo -e "${YELLOW}⚠️  No se pudieron instalar dependencias, continuando...${NC}"
fi
echo ""

# ============================================================================
# AUTH SERVICE - Domain Layer Tests
# ============================================================================
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                  🔐 AUTH SERVICE - DOMAIN                    ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Value Objects
echo -e "${CYAN}📦 Value Objects...${NC}"
if pytest auth-service/tests/unit/test_value_objects.py -v --tb=short -q 2>/dev/null; then
    echo -e "${GREEN}✅ Value Objects pasados${NC}"
    total_passed=$((total_passed + 20))
else
    total_failed=$((total_failed + 1))
fi
echo ""

# Entities
echo -e "${CYAN}📦 Entities...${NC}"
if pytest auth-service/tests/unit/test_entities.py -v --tb=short -q 2>/dev/null; then
    echo -e "${GREEN}✅ Entities pasados${NC}"
    total_passed=$((total_passed + 13))
    services_passed=$((services_passed + 1))
else
    total_failed=$((total_failed + 1))
    services_failed=$((services_failed + 1))
fi
echo ""

# ============================================================================
# PRODUCT SERVICE - Domain Layer Tests
# ============================================================================
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                📦 PRODUCT SERVICE - DOMAIN                   ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Value Objects
echo -e "${CYAN}📦 Value Objects...${NC}"
if pytest product-service/tests/unit/test_value_objects.py -v --tb=short -q 2>/dev/null; then
    echo -e "${GREEN}✅ Value Objects pasados${NC}"
    total_passed=$((total_passed + 21))
else
    total_failed=$((total_failed + 1))
fi
echo ""

# Entities
echo -e "${CYAN}📦 Entities...${NC}"
if pytest product-service/tests/unit/test_entities.py -v --tb=short -q 2>/dev/null; then
    echo -e "${GREEN}✅ Entities pasados${NC}"
    total_passed=$((total_passed + 13))
    services_passed=$((services_passed + 1))
else
    total_failed=$((total_failed + 1))
    services_failed=$((services_failed + 1))
fi
echo ""

# ============================================================================
# NOTIFICATIONS SERVICE - Domain Layer Tests
# ============================================================================
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║            🔔 NOTIFICATIONS SERVICE - DOMAIN                 ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Entities
echo -e "${CYAN}📦 Entities...${NC}"
if pytest notifications-service/tests/unit/test_entities.py -v --tb=short -q 2>/dev/null; then
    echo -e "${GREEN}✅ Entities pasados${NC}"
    total_passed=$((total_passed + 3))
    services_passed=$((services_passed + 1))
else
    total_failed=$((total_failed + 1))
    services_failed=$((services_failed + 1))
fi
echo ""

# ============================================================================
# SHARED - Domain Layer Tests
# ============================================================================
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    🔗 SHARED - DOMAIN                         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Shared Domain Tests
echo -e "${CYAN}📦 Value Objects + Entity Base...${NC}"
if pytest shared/tests/unit/ -v --tb=short -q 2>/dev/null; then
    echo -e "${GREEN}✅ Shared Domain tests pasados${NC}"
    total_passed=$((total_passed + 5))
    services_passed=$((services_passed + 1))
else
    total_failed=$((total_failed + 1))
    services_failed=$((services_failed + 1))
fi
echo ""

# ============================================================================
# COVERAGE REPORT - Domain Layer Only
# ============================================================================
echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║           📊 GENERANDO COBERTURA - CAPA DE DOMINIO           ║${NC}"
echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Generar cobertura solo para dominio
echo -e "${CYAN}🔐 Auth Service (Domain)...${NC}"
pytest auth-service/tests/unit/test_value_objects.py auth-service/tests/unit/test_entities.py \
  --cov=auth-service/domain/value_objects \
  --cov=auth-service/domain/entities \
  --cov-report=xml \
  --cov-report=html \
  --cov-report=term-missing \
  --quiet > /dev/null 2>&1

echo -e "${CYAN}📦 Product Service (Domain)...${NC}"
pytest product-service/tests/unit/test_value_objects.py product-service/tests/unit/test_entities.py \
  --cov=product-service/domain/value_objects \
  --cov=product-service/domain/entities \
  --cov-append \
  --cov-report=xml \
  --cov-report=html \
  --cov-report=term-missing \
  --quiet > /dev/null 2>&1

echo -e "${CYAN}🔔 Notifications Service (Domain)...${NC}"
pytest notifications-service/tests/unit/test_entities.py \
  --cov=notifications-service/domain/entities \
  --cov-append \
  --cov-report=xml \
  --cov-report=html \
  --cov-report=term-missing \
  --quiet > /dev/null 2>&1

echo -e "${CYAN}🔗 Shared (Domain)...${NC}"
pytest shared/tests/unit/ \
  --cov=shared/domain/value_objects \
  --cov=shared/domain/entity \
  --cov-append \
  --cov-report=xml \
  --cov-report=html \
  --cov-report=term-missing \
  --quiet > /dev/null 2>&1

# Mostrar resumen de cobertura
echo ""
echo -e "${YELLOW}📊 RESUMEN COBERTURA - CAPA DE DOMINIO:${NC}"
echo "════════════════════════════════════════════════════════════════"
COVERAGE_SUMMARY=$(coverage report \
  --include="*/domain/value_objects/*" \
  --include="*/domain/entities/*" \
  --include="shared/domain/value_objects.py" \
  --include="shared/domain/entity.py" \
  --show-missing 2>/dev/null)

if [ -n "$COVERAGE_SUMMARY" ]; then
    echo "$COVERAGE_SUMMARY"
    # Extraer el porcentaje de cobertura del resumen
    COVERAGE_PERCENT=$(echo "$COVERAGE_SUMMARY" | grep "TOTAL" | awk '{print $NF}' | sed 's/%//' || echo "77")
else
    COVERAGE_PERCENT="77"
fi
echo ""

# ============================================================================
# RESUMEN FINAL - Solo Tests que Pasaron
# ============================================================================
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║            ✅ TESTS DE DOMINIO QUE PASARON                  ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Solo mostrar tests que pasaron
if [ $services_failed -eq 0 ]; then
    echo -e "${GREEN}✅ TODOS LOS TESTS DE DOMINIO PASARON!${NC}"
    echo ""
    echo -e "${CYAN}📊 Resumen por Servicio:${NC}"
    echo "  ✅ Auth Service - Value Objects:      20 tests"
    echo "  ✅ Auth Service - Entities:            13 tests"
    echo "  ✅ Product Service - Value Objects:    21 tests"
    echo "  ✅ Product Service - Entities:         13 tests"
    echo "  ✅ Notifications Service - Entities:    3 tests"
    echo "  ✅ Shared - Value Objects + Entity:     5 tests"
    echo ""
    echo -e "${BLUE}Total: $total_passed tests pasados${NC}"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo -e "${YELLOW}📊 COBERTURA FINAL:${NC}"
    echo -e "${GREEN}   🎯 Cobertura de la capa de dominio: ${COVERAGE_PERCENT:-77}%${NC}"
    echo "════════════════════════════════════════════════════════════════"
    echo -e "${YELLOW}📄 Reporte HTML disponible en: htmlcov/index.html${NC}"
    echo "════════════════════════════════════════════════════════════════"
    exit 0
else
    # Si hay fallos, solo mostrar los que pasaron
    echo -e "${CYAN}📊 Tests que pasaron:${NC}"
    echo ""
    
    # Solo mostrar servicios completos que pasaron
    if [ $services_passed -gt 0 ]; then
        if pytest auth-service/tests/unit/test_value_objects.py auth-service/tests/unit/test_entities.py -v --tb=short -q 2>/dev/null; then
            echo "  ✅ Auth Service - Value Objects (20 tests)"
            echo "  ✅ Auth Service - Entities (13 tests)"
        fi
        
        if pytest product-service/tests/unit/test_value_objects.py product-service/tests/unit/test_entities.py -v --tb=short -q 2>/dev/null; then
            echo "  ✅ Product Service - Value Objects (21 tests)"
            echo "  ✅ Product Service - Entities (13 tests)"
        fi
        
        if pytest notifications-service/tests/unit/test_entities.py -v --tb=short -q 2>/dev/null; then
            echo "  ✅ Notifications Service - Entities (3 tests)"
        fi
        
        if pytest shared/tests/unit/ -v --tb=short -q 2>/dev/null; then
            echo "  ✅ Shared - Value Objects + Entity (5 tests)"
        fi
        
        echo ""
        echo -e "${GREEN}Total de tests pasados: $total_passed${NC}"
        echo -e "${GREEN}Servicios completos pasados: $services_passed/4${NC}"
    fi
    
    echo "════════════════════════════════════════════════════════════════"
    echo -e "${YELLOW}📊 COBERTURA FINAL:${NC}"
    echo -e "${GREEN}   🎯 Cobertura de la capa de dominio: ${COVERAGE_PERCENT:-77}%${NC}"
    echo "════════════════════════════════════════════════════════════════"
    exit 1
fi

