#!/bin/bash

# Script para probar el pipeline localmente antes de ejecutarlo en GitHub Actions
# Uso: ./test-pipeline-local.sh

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

echo "🚀 PRUEBA LOCAL DEL PIPELINE GITHUB ACTIONS"
echo "=============================================="
echo ""

# Paso 1: Verificar estructura del proyecto
log "Paso 1: Verificando estructura del proyecto..."
if [ ! -f ".github/workflows/deploy-ecs.yml" ]; then
    error "Archivo deploy-ecs.yml no encontrado"
    exit 1
fi

if [ ! -d "terraform" ]; then
    error "Directorio terraform no encontrado"
    exit 1
fi

if [ ! -f "apiMS/microservices/requirements.txt" ]; then
    error "Archivo requirements.txt no encontrado"
    exit 1
fi

success "Estructura del proyecto verificada"

# Paso 2: Verificar archivos de Terraform
log "Paso 2: Verificando archivos de Terraform..."
cd terraform

if [ ! -f "main.tf" ] || [ ! -f "variables.tf" ] || [ ! -f "outputs.tf" ]; then
    error "Archivos de Terraform incompletos"
    exit 1
fi

# Verificar sintaxis de Terraform
if ! terraform fmt -check -recursive . > /dev/null 2>&1; then
    warning "Corrigiendo formato de Terraform..."
    terraform fmt -recursive .
fi

# Inicializar Terraform
if ! terraform init > /dev/null 2>&1; then
    error "Error al inicializar Terraform"
    exit 1
fi

# Validar configuración
if ! terraform validate > /dev/null 2>&1; then
    error "Configuración de Terraform inválida"
    exit 1
fi

success "Archivos de Terraform verificados"

cd ..

# Paso 3: Verificar tests
log "Paso 3: Verificando tests unitarios..."
cd apiMS/microservices

# Configurar PYTHONPATH
export PYTHONPATH=$(pwd)

# Verificar que los tests existen
if [ ! -d "auth-service/tests/unit" ] || [ ! -d "product-service/tests/unit" ]; then
    error "Directorios de tests no encontrados"
    exit 1
fi

# Ejecutar tests de Auth Service
log "Ejecutando tests de Auth Service..."
if ! pytest auth-service/tests/unit/test_value_objects.py auth-service/tests/unit/test_entities.py -q > /dev/null 2>&1; then
    error "Tests de Auth Service fallaron"
    exit 1
fi

# Ejecutar tests de Product Service
log "Ejecutando tests de Product Service..."
if ! pytest product-service/tests/unit/ -q > /dev/null 2>&1; then
    error "Tests de Product Service fallaron"
    exit 1
fi

success "Tests unitarios verificados"

cd ../..

# Paso 4: Verificar Dockerfiles
log "Paso 4: Verificando Dockerfiles..."
if [ ! -f "apiMS/microservices/auth-service/Dockerfile" ] || [ ! -f "apiMS/microservices/product-service/Dockerfile" ]; then
    error "Dockerfiles no encontrados"
    exit 1
fi

success "Dockerfiles verificados"

# Paso 5: Verificar archivos de requirements
log "Paso 5: Verificando archivos de requirements..."
if [ ! -f "apiMS/microservices/requirements.txt" ] || [ ! -f "apiMS/microservices/requirements-test.txt" ]; then
    error "Archivos de requirements no encontrados"
    exit 1
fi

success "Archivos de requirements verificados"

# Paso 6: Verificar configuración de GitHub Actions
log "Paso 6: Verificando configuración de GitHub Actions..."
if ! grep -q "AWS_ACCESS_KEY_ID" .github/workflows/deploy-ecs.yml; then
    error "Configuración de AWS credentials no encontrada en el pipeline"
    exit 1
fi

if ! grep -q "terraform" .github/workflows/deploy-ecs.yml; then
    error "Configuración de Terraform no encontrada en el pipeline"
    exit 1
fi

success "Configuración de GitHub Actions verificada"

# Resumen final
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║            ✅ PIPELINE LISTO PARA GITHUB ACTIONS             ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Próximos pasos:"
echo "1. Configurar GitHub Secrets:"
echo "   - AWS_ACCESS_KEY_ID"
echo "   - AWS_SECRET_ACCESS_KEY"
echo "   - AWS_ACCOUNT_ID"
echo ""
echo "2. Hacer commit y push:"
echo "   git add ."
echo "   git commit -m 'Add ECS deployment pipeline'"
echo "   git push origin main"
echo ""
echo "3. O ejecutar manualmente en GitHub Actions"
echo ""
echo "🎉 ¡Pipeline listo para ejecutar!"
