#!/bin/bash
# Script para ejecutar todos los tests

echo "🧪 Ejecutando Tests Unitarios - Arquitectura Hexagonal"
echo "======================================================"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Instalar dependencias de testing si no están instaladas
echo -e "${YELLOW}📦 Verificando dependencias de testing...${NC}"
pip install -q -r requirements-test.txt

# Ejecutar tests
echo -e "\n${GREEN}🧪 Ejecutando tests unitarios...${NC}"
pytest -v --tb=short -m unit

# Verificar resultado
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Todos los tests pasaron!${NC}"
else
    echo -e "\n${RED}❌ Algunos tests fallaron${NC}"
    exit 1
fi

# Generar reporte de cobertura
echo -e "\n${YELLOW}📊 Generando reporte de cobertura...${NC}"
pytest --cov=auth-service --cov=product-service --cov-report=html --cov-report=term-missing -m unit

echo -e "\n${GREEN}✅ Tests completados!${NC}"
echo -e "${YELLOW}📄 Reporte HTML disponible en: htmlcov/index.html${NC}"

