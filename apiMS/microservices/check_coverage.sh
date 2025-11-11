#!/bin/bash
# Script para verificar cobertura de código y identificar módulos con menos del 70%

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║         📊 VERIFICACIÓN DE COBERTURA DE CÓDIGO               ║"
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

THRESHOLD=70
MODULES_BELOW_THRESHOLD=0

# Función para verificar cobertura de un servicio
check_service_coverage() {
    local SERVICE=$1
    local TEST_PATH=$2
    local COV_PATH=$3
    
    echo -e "${CYAN}📦 Verificando $SERVICE...${NC}"
    
    # Verificar si los archivos de test existen
    for test_file in $TEST_PATH; do
        if [ ! -f "$test_file" ]; then
            echo -e "${YELLOW}⚠️  Archivo de test no encontrado: $test_file${NC}"
            echo -e "${YELLOW}   Este módulo no tiene tests aún${NC}"
            MODULES_BELOW_THRESHOLD=$((MODULES_BELOW_THRESHOLD + 1))
            echo ""
            return 1
        fi
    done
    
    # Ejecutar pytest y capturar salida
    local TMP_FILE="/tmp/coverage_${SERVICE// /_}.txt"
    
    # Ejecutar pytest sin --cov-fail-under para capturar el porcentaje aunque sea bajo
    # Capturar tanto salida estándar como errores
    pytest $TEST_PATH --cov="$COV_PATH" --cov-report=term-missing --quiet --tb=no > "$TMP_FILE" 2>&1
    PYTEST_EXIT=$?
    
    # Verificar si el archivo de cobertura se generó (incluso si algunos tests fallaron)
    if [ -f "$TMP_FILE" ] && grep -q "TOTAL\|Cover" "$TMP_FILE" 2>/dev/null; then
        # Extraer porcentaje de cobertura del módulo específico
        # Buscar líneas que comiencen con el COV_PATH y extraer el porcentaje (última columna)
        MODULE_LINES=$(grep -E "^${COV_PATH}" "$TMP_FILE" 2>/dev/null | grep -v "^$" || echo "")
        
        if [ -n "$MODULE_LINES" ]; then
            # Extraer porcentajes (última columna que termina en %)
            MODULE_COVERAGE=$(echo "$MODULE_LINES" | awk '{print $NF}' | grep -E "[0-9]+%" | sed 's/%//' | awk '{sum+=$1; count++} END {if(count>0) printf "%.0f", sum/count; else print "0"}')
            
            # Si no encontramos porcentajes válidos, intentar calcular desde la columna de cobertura (normalmente columna 4)
            if [ "$MODULE_COVERAGE" = "0" ] || [ -z "$MODULE_COVERAGE" ]; then
                MODULE_COVERAGE=$(echo "$MODULE_LINES" | awk '{if($4 ~ /[0-9]+%/) print $4; else if($3 ~ /[0-9]+%/) print $3}' | sed 's/%//' | awk '{sum+=$1; count++} END {if(count>0) printf "%.0f", sum/count; else print "0"}')
            fi
        fi
        
        # Si aún no encontramos cobertura, usar TOTAL como fallback
        if [ "$MODULE_COVERAGE" = "0" ] || [ -z "$MODULE_COVERAGE" ]; then
            MODULE_COVERAGE=$(grep "TOTAL" "$TMP_FILE" | tail -1 | awk '{print $NF}' | sed 's/%//' || echo "0")
        fi
        
        # Verificar si bc está disponible para comparación numérica
        if command -v bc &> /dev/null && [ -n "$MODULE_COVERAGE" ] && [ "$MODULE_COVERAGE" != "0" ]; then
            if (( $(echo "$MODULE_COVERAGE < $THRESHOLD" | bc -l 2>/dev/null) )); then
                echo -e "${RED}⚠️  $SERVICE: ${MODULE_COVERAGE}% (menor al ${THRESHOLD}% requerido)${NC}"
                MODULES_BELOW_THRESHOLD=$((MODULES_BELOW_THRESHOLD + 1))
                
                # Mostrar módulos específicos con baja cobertura
                echo -e "${YELLOW}   Módulos que necesitan más tests:${NC}"
                grep -E "^${COV_PATH}" "$TMP_FILE" 2>/dev/null | \
                    awk -v threshold="$THRESHOLD" '{
                        # Extraer porcentaje de la última columna o columna que tenga %
                        coverage = ($NF ~ /[0-9]+%/) ? $NF : (($4 ~ /[0-9]+%/) ? $4 : "");
                        if (coverage != "") {
                            coverage_num = coverage;
                            gsub(/%/, "", coverage_num);
                            if (coverage_num < threshold) {
                                print "   - " $1 ": " coverage;
                            }
                        }
                    }' || true
            else
                echo -e "${GREEN}✅ $SERVICE: ${MODULE_COVERAGE}%${NC}"
            fi
        elif [ -n "$MODULE_COVERAGE" ] && [ "$MODULE_COVERAGE" != "0" ]; then
            # Fallback sin bc: comparación simple (solo parte entera)
            COVERAGE_INT=${MODULE_COVERAGE%.*}
            if [ "$COVERAGE_INT" -lt "$THRESHOLD" ] 2>/dev/null; then
                echo -e "${RED}⚠️  $SERVICE: ${MODULE_COVERAGE}% (menor al ${THRESHOLD}% requerido)${NC}"
                MODULES_BELOW_THRESHOLD=$((MODULES_BELOW_THRESHOLD + 1))
            else
                echo -e "${GREEN}✅ $SERVICE: ${MODULE_COVERAGE}%${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  No se pudo determinar cobertura para $SERVICE${NC}"
            MODULES_BELOW_THRESHOLD=$((MODULES_BELOW_THRESHOLD + 1))
        fi
        
        # Mostrar advertencia si pytest falló pero aún así generó cobertura
        if [ $PYTEST_EXIT -ne 0 ]; then
            FAILED_TESTS=$(grep -E "FAILED|ERROR" "$TMP_FILE" 2>/dev/null | wc -l | tr -d ' ')
            if [ "$FAILED_TESTS" -gt 0 ]; then
                echo -e "${YELLOW}   ⚠️  Algunos tests fallaron ($FAILED_TESTS), pero se calculó cobertura${NC}"
            fi
        fi
    else
        # No se pudo generar reporte de cobertura
        ERROR_MSG=$(grep -iE "error|failed|not found|ImportError|ModuleNotFoundError" "$TMP_FILE" 2>/dev/null | head -3 | tr '\n' ' ' || echo "Error al ejecutar tests")
        echo -e "${RED}❌ Error al ejecutar tests de $SERVICE${NC}"
        if [ -n "$ERROR_MSG" ] && [ "$ERROR_MSG" != "Error al ejecutar tests" ]; then
            echo -e "${YELLOW}   Detalle: ${ERROR_MSG}${NC}"
        fi
        MODULES_BELOW_THRESHOLD=$((MODULES_BELOW_THRESHOLD + 1))
    fi
    
    # Limpiar archivo temporal
    rm -f "$TMP_FILE" 2>/dev/null
    echo ""
}

# Verificar dependencias
echo -e "${YELLOW}📦 Verificando dependencias de testing...${NC}"
pip install -q -r requirements-test.txt 2>/dev/null || echo -e "${YELLOW}⚠️  Algunas dependencias no se pudieron instalar${NC}"
echo ""

# Verificar cada servicio (solo los que tienen tests)
check_service_coverage "Auth Service (Domain)" "auth-service/tests/unit/test_value_objects.py auth-service/tests/unit/test_entities.py" "auth-service/domain"

# Verificar si test_command_handlers existe antes de intentar ejecutarlo
if [ -f "auth-service/tests/unit/test_command_handlers.py" ]; then
    check_service_coverage "Auth Service (Application)" "auth-service/tests/unit/test_command_handlers.py" "auth-service/application"
else
    echo -e "${CYAN}📦 Verificando Auth Service (Application)...${NC}"
    echo -e "${YELLOW}⚠️  No hay tests para Auth Service Application aún${NC}"
    MODULES_BELOW_THRESHOLD=$((MODULES_BELOW_THRESHOLD + 1))
    echo ""
fi

check_service_coverage "Product Service (Domain)" "product-service/tests/unit/test_value_objects.py product-service/tests/unit/test_entities.py" "product-service/domain"

if [ -f "order-service/tests/unit/test_commands_queries.py" ]; then
    check_service_coverage "Order Service (Application)" "order-service/tests/unit/test_commands_queries.py" "order-service/application"
else
    echo -e "${CYAN}📦 Verificando Order Service (Application)...${NC}"
    echo -e "${YELLOW}⚠️  No hay tests para Order Service Application aún${NC}"
    MODULES_BELOW_THRESHOLD=$((MODULES_BELOW_THRESHOLD + 1))
    echo ""
fi

if [ -f "logistics-service/tests/unit/test_commands_queries.py" ]; then
    check_service_coverage "Logistics Service (Application)" "logistics-service/tests/unit/test_commands_queries.py" "logistics-service/application"
else
    echo -e "${CYAN}📦 Verificando Logistics Service (Application)...${NC}"
    echo -e "${YELLOW}⚠️  No hay tests para Logistics Service Application aún${NC}"
    MODULES_BELOW_THRESHOLD=$((MODULES_BELOW_THRESHOLD + 1))
    echo ""
fi

if [ -f "notifications-service/tests/unit/test_entities.py" ]; then
    check_service_coverage "Notifications Service (Domain)" "notifications-service/tests/unit/test_entities.py" "notifications-service/domain"
else
    echo -e "${CYAN}📦 Verificando Notifications Service (Domain)...${NC}"
    echo -e "${YELLOW}⚠️  No hay tests para Notifications Service Domain aún${NC}"
    MODULES_BELOW_THRESHOLD=$((MODULES_BELOW_THRESHOLD + 1))
    echo ""
fi

if [ -d "shared/tests/unit" ] && [ -n "$(find shared/tests/unit -name 'test_*.py' 2>/dev/null | head -1)" ]; then
    # Usar find para obtener archivos de test
    TEST_FILES=$(find shared/tests/unit -name 'test_*.py' 2>/dev/null | tr '\n' ' ')
    check_service_coverage "Shared (Domain)" "$TEST_FILES" "shared/domain"
else
    echo -e "${CYAN}📦 Verificando Shared (Domain)...${NC}"
    echo -e "${YELLOW}⚠️  No hay tests para Shared Domain aún${NC}"
    MODULES_BELOW_THRESHOLD=$((MODULES_BELOW_THRESHOLD + 1))
    echo ""
fi

# Resumen final
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║                   📊 RESUMEN FINAL                            ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

if [ $MODULES_BELOW_THRESHOLD -eq 0 ]; then
    echo -e "${GREEN}✅ Todos los módulos tienen cobertura >= ${THRESHOLD}%${NC}"
    echo ""
    echo -e "${YELLOW}💡 Recomendación:${NC}"
    echo "   - Continúa agregando tests para mantener la cobertura alta"
    echo "   - Considera agregar tests de integración para las capas faltantes"
    exit 0
else
    echo -e "${RED}⚠️  $MODULES_BELOW_THRESHOLD módulo(s) tienen cobertura < ${THRESHOLD}%${NC}"
    echo ""
    echo -e "${YELLOW}💡 Recomendaciones:${NC}"
    echo "   1. Revisa los módulos listados arriba"
    echo "   2. Agrega tests unitarios para los módulos con baja cobertura"
    echo "   3. Prioriza tests para Application Handlers y Repositories"
    echo "   4. Ejecuta este script nuevamente después de agregar tests"
    echo ""
    echo -e "${CYAN}📚 Guía para aumentar cobertura:${NC}"
    echo "   - Application Handlers: Test cada handler con casos exitosos y de error"
    echo "   - Repositories: Test métodos CRUD y consultas"
    echo "   - API Routes: Test endpoints con diferentes casos"
    echo "   - Services: Test lógica de negocio y validaciones"
    exit 1
fi

