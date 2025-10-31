#!/bin/bash

# ==============================================================================
# Script de Despliegue a GCP
# ==============================================================================
# Este script despliega la infraestructura usando Terraform
# ==============================================================================

set -e

echo "🚀 Despliegue de Microservicios MediSupply a GCP"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar que Terraform está instalado
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Error: Terraform no está instalado${NC}"
    echo "Instala desde: https://www.terraform.io/downloads"
    exit 1
fi

# Verificar que terraform.tfvars existe
if [ ! -f "terraform.tfvars" ]; then
    echo -e "${YELLOW}⚠️  terraform.tfvars no existe${NC}"
    echo "Copia terraform.tfvars.example y configura tus valores"
    exit 1
fi

# Verificar que las imágenes Docker existen
echo ""
echo "🔍 Verificando que las imágenes Docker existen..."
PROJECT_ID=$(grep -E '^project_id\s*=' terraform.tfvars | cut -d'"' -f2)
REGION=$(grep -E '^region\s*=' terraform.tfvars | cut -d'"' -f2 || echo "us-central1")
REPO="${PROJECT_ID}-docker-repo"

# Verificar si las imágenes existen
if ! gcloud artifacts docker images list \
  --repository=${REPO} \
  --location=${REGION} \
  --filter="package:auth-service" \
  --format="value(package)" | grep -q "auth-service"; then
    echo -e "${YELLOW}⚠️  Las imágenes Docker no existen en Artifact Registry${NC}"
    echo ""
    read -p "¿Quieres construir y subir las imágenes ahora? (y/n): " BUILD_IMAGES
    
    if [ "$BUILD_IMAGES" = "y" ]; then
        echo ""
        echo "🐳 Construyendo y subiendo imágenes..."
        ./build-and-push-images.sh
        echo ""
        echo "✅ Imágenes construidas y subidas!"
    else
        echo ""
        echo "Ejecuta primero: ./build-and-push-images.sh"
        exit 1
    fi
fi

# Confirmar despliegue
echo -e "${YELLOW}⚠️  Estás a punto de desplegar infraestructura a GCP${NC}"
read -p "¿Continuar? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "Cancelado"
    exit 0
fi

# Inicializar Terraform
echo ""
echo "🔧 Inicializando Terraform..."
terraform init

# Validar configuración
echo ""
echo "✅ Validando configuración..."
terraform validate

# Mostrar plan
echo ""
echo "📋 Mostrando plan de ejecución..."
terraform plan

# Confirmar aplicación
echo ""
read -p "¿Aplicar estos cambios? (y/n): " APPLY

if [ "$APPLY" != "y" ]; then
    echo "Cancelado"
    exit 0
fi

# Aplicar cambios
echo ""
echo "🚀 Aplicando cambios..."
terraform apply -auto-approve

# Mostrar outputs
echo ""
echo -e "${GREEN}✅ Despliegue completado!${NC}"
echo ""
echo "📊 URLs de Servicios:"
echo ""
terraform output services_info

echo ""
echo "🏥 Verificando salud de servicios..."
echo ""

AUTH_URL=$(terraform output -raw auth_service_url)
PRODUCT_URL=$(terraform output -raw product_service_url)

# Health checks
echo "Auth Service:"
curl -f "$AUTH_URL/health" && echo " ✅" || echo " ❌"

echo "Product Service:"
curl -f "$PRODUCT_URL/health" && echo " ✅" || echo " ❌"

echo ""
echo -e "${GREEN}🎉 ¡Despliegue exitoso!${NC}"
echo ""

