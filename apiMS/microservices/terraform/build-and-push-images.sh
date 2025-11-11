#!/bin/bash

# ==============================================================================
# Script para construir y subir imágenes Docker a Artifact Registry
# ==============================================================================
# Ejecuta este script ANTES de ejecutar terraform apply
# ==============================================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🐳 Construyendo y subiendo imágenes Docker a Artifact Registry"
echo ""

# Cargar variables de terraform.tfvars si existe
if [ ! -f "terraform.tfvars" ]; then
    echo -e "${RED}❌ Error: terraform.tfvars no existe${NC}"
    echo "Crea terraform.tfvars primero o configura estas variables:"
    echo "  PROJECT_ID=tu-proyecto-id"
    echo "  REGION=us-central1"
    exit 1
fi

# Leer variables de terraform.tfvars
PROJECT_ID=$(grep -E '^project_id\s*=' terraform.tfvars | cut -d'"' -f2)
REGION=$(grep -E '^region\s*=' terraform.tfvars | cut -d'"' -f2 || echo "us-central1")
REPOSITORY="${PROJECT_ID}-docker-repo"

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Error: PROJECT_ID no encontrado en terraform.tfvars${NC}"
    exit 1
fi

echo "📋 Configuración:"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Repository: $REPOSITORY"
echo ""

# Verificar que gcloud está autenticado
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  No estás autenticado en gcloud${NC}"
    echo "Ejecuta: gcloud auth login"
    exit 1
fi

# Configurar proyecto
gcloud config set project $PROJECT_ID

# Habilitar APIs si es necesario
echo "🔌 Verificando APIs..."
gcloud services enable \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  --project=$PROJECT_ID

# Configurar Docker para Artifact Registry
echo ""
echo "🔧 Configurando Docker para Artifact Registry..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# Cambiar al directorio de microservicios
cd ..

# Construir y subir imágenes
SERVICES=("auth-service" "product-service" "order-service" "logistics-service" "notifications-service")

for SERVICE in "${SERVICES[@]}"; do
    echo ""
    echo "📦 Construyendo $SERVICE..."
    
    IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE}"
    
    docker build \
      --platform linux/amd64 \
      -f ${SERVICE}/Dockerfile \
      -t ${IMAGE_TAG}:latest \
      -t ${IMAGE_TAG}:${GITHUB_SHA:-$(date +%s)} \
      .
    
    echo "📤 Subiendo $SERVICE..."
    docker push ${IMAGE_TAG}:latest
    docker push ${IMAGE_TAG}:${GITHUB_SHA:-$(date +%s)} || true
    
    echo -e "${GREEN}✅ $SERVICE completado${NC}"
done

echo ""
echo -e "${GREEN}🎉 Todas las imágenes han sido construidas y subidas!${NC}"
echo ""
echo "Ahora puedes ejecutar: terraform apply"

