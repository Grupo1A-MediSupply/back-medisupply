#!/bin/bash

# ==============================================================================
# Script para probar el pipeline de GitHub Actions localmente
# ==============================================================================
# Este script simula los pasos del workflow deploy-gcp.yml
# ==============================================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    🧪 Prueba Local del Pipeline de Despliegue GCP${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Cargar configuración
cd "$(dirname "$0")"
SCRIPT_DIR=$(pwd)
cd "$SCRIPT_DIR/.."

# Verificar terraform.tfvars
if [ ! -f "terraform/terraform.tfvars" ]; then
    echo -e "${RED}❌ Error: terraform.tfvars no existe${NC}"
    exit 1
fi

# Leer configuración
PROJECT_ID=$(grep -E '^project_id\s*=' terraform/terraform.tfvars | cut -d'"' -f2)
REGION=$(grep -E '^region\s*=' terraform/terraform.tfvars | cut -d'"' -f2 || echo "us-central1")
REPOSITORY="${PROJECT_ID}-docker-repo"

echo -e "${GREEN}📋 Configuración:${NC}"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Repository: $REPOSITORY"
echo ""

# Verificar herramientas
echo -e "${BLUE}🔍 Verificando herramientas...${NC}"
command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker no está instalado${NC}"; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo -e "${RED}❌ Terraform no está instalado${NC}"; exit 1; }
command -v gcloud >/dev/null 2>&1 || { echo -e "${RED}❌ gcloud no está instalado${NC}"; exit 1; }
echo -e "${GREEN}✅ Todas las herramientas están instaladas${NC}"
echo ""

# Verificar Docker
if ! docker ps >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker daemon no está corriendo${NC}"
    echo "Inicia Docker Desktop y vuelve a intentar"
    exit 1
fi
echo -e "${GREEN}✅ Docker está corriendo${NC}"
echo ""

# ============================================================================
# JOB 1: Build and Push Docker Images
# ============================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  📦 JOB 1: Build and Push Docker Images${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Verificar autenticación GCP
echo "🔐 Verificando autenticación GCP..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  No estás autenticado en GCP${NC}"
    echo "Ejecuta: gcloud auth login"
    exit 1
fi
echo -e "${GREEN}✅ Autenticado en GCP${NC}"
echo ""

# Configurar proyecto
echo "🔧 Configurando proyecto GCP..."
gcloud config set project $PROJECT_ID >/dev/null 2>&1
echo -e "${GREEN}✅ Proyecto configurado${NC}"
echo ""

# Configurar Docker para Artifact Registry
echo "🐳 Configurando Docker para Artifact Registry..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet
echo -e "${GREEN}✅ Docker configurado${NC}"
echo ""

# Verificar/Crear Artifact Registry
echo "🔍 Verificando Artifact Registry..."
if ! gcloud artifacts repositories describe $REPOSITORY --location=$REGION >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Artifact Registry no existe, creándolo...${NC}"
    gcloud artifacts repositories create $REPOSITORY \
      --repository-format=docker \
      --location=$REGION \
      --description="Docker repository for MediSupply microservices"
    echo -e "${GREEN}✅ Artifact Registry creado${NC}"
else
    echo -e "${GREEN}✅ Artifact Registry existe${NC}"
fi
echo ""

# Construir y subir imágenes
SERVICES=("auth-service" "product-service" "order-service" "logistics-service" "notifications-service")
IMAGE_BASE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}"

for SERVICE in "${SERVICES[@]}"; do
    echo -e "${BLUE}📦 Construyendo ${SERVICE}...${NC}"
    docker build \
      --platform linux/amd64 \
      -f ${SERVICE}/Dockerfile \
      -t ${IMAGE_BASE}/${SERVICE}:latest \
      -t ${IMAGE_BASE}/${SERVICE}:test \
      . >/dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✅ ${SERVICE} construido${NC}"
    else
        echo -e "${RED}  ❌ Error construyendo ${SERVICE}${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}📤 Subiendo ${SERVICE}...${NC}"
    docker push ${IMAGE_BASE}/${SERVICE}:latest >/dev/null 2>&1
    docker push ${IMAGE_BASE}/${SERVICE}:test >/dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✅ ${SERVICE} subido${NC}"
    else
        echo -e "${RED}  ❌ Error subiendo ${SERVICE}${NC}"
        exit 1
    fi
    echo ""
done

echo -e "${GREEN}✅ Todas las imágenes construidas y subidas${NC}"
echo ""

# ============================================================================
# JOB 2: Deploy with Terraform
# ============================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🚀 JOB 2: Deploy with Terraform${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

cd terraform

# Terraform Init
echo "🔧 Inicializando Terraform..."
terraform init >/dev/null 2>&1
echo -e "${GREEN}✅ Terraform inicializado${NC}"
echo ""

# Terraform Validate
echo "✅ Validando configuración de Terraform..."
if terraform validate >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Configuración válida${NC}"
else
    echo -e "${RED}❌ Error en la configuración${NC}"
    terraform validate
    exit 1
fi
echo ""

# Terraform Plan
echo "📋 Generando plan de Terraform..."
if terraform plan -out=tfplan >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Plan generado${NC}"
else
    echo -e "${RED}❌ Error generando plan${NC}"
    terraform plan
    exit 1
fi
echo ""

# Mostrar qué se va a crear
echo "📊 Cambios planificados:"
terraform show -json tfplan 2>/dev/null | python3 -c "
import sys, json
plan = json.load(sys.stdin)
resources = plan.get('resource_changes', [])
creates = [r for r in resources if r['change']['actions'] == ['create']]
updates = [r for r in resources if r['change']['actions'] == ['update']]
print(f'  Crear: {len(creates)} recursos')
print(f'  Actualizar: {len(updates)} recursos')
" 2>/dev/null || terraform plan tfplan | grep -E "(will be|will be updated)" | head -5

echo ""

# Verificar si hay cambios
CHANGES=$(terraform show -json tfplan 2>/dev/null | python3 -c "import sys, json; plan=json.load(sys.stdin); resources=plan.get('resource_changes', []); creates=len([r for r in resources if r['change']['actions']==['create']]); updates=len([r for r in resources if r['change']['actions']==['update']]); print(creates+updates)" 2>/dev/null || echo "1")

if [ "$CHANGES" = "0" ]; then
    echo -e "${GREEN}✅ No hay cambios pendientes - infraestructura actualizada${NC}"
    echo ""
else
    # Preguntar si aplicar
    read -p "¿Quieres aplicar estos cambios? (y/n): " APPLY
    
    if [ "$APPLY" != "y" ]; then
        echo -e "${YELLOW}⚠️  Despliegue cancelado${NC}"
        echo "Para aplicar más tarde: cd terraform && terraform apply tfplan"
        exit 0
    fi
fi

# Terraform Apply (solo si hay cambios)
if [ "$CHANGES" != "0" ]; then
    echo ""
    echo "🚀 Aplicando cambios con Terraform..."
    if terraform apply -auto-approve tfplan; then
        echo -e "${GREEN}✅ Despliegue completado${NC}"
    else
        echo -e "${RED}❌ Error en el despliegue${NC}"
        exit 1
    fi
fi

echo ""

# ============================================================================
# JOB 3: Health Check
# ============================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🏥 JOB 3: Health Check${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

echo "🔍 Verificando salud de servicios..."
echo ""

# Obtener URLs
AUTH_URL=$(terraform output -raw auth_service_url 2>/dev/null || echo "")
PRODUCT_URL=$(terraform output -raw product_service_url 2>/dev/null || echo "")
ORDER_URL=$(terraform output -raw order_service_url 2>/dev/null || echo "")
LOGISTICS_URL=$(terraform output -raw logistics_service_url 2>/dev/null || echo "")
NOTIFICATIONS_URL=$(terraform output -raw notifications_service_url 2>/dev/null || echo "")

# Health checks
check_service() {
    local name=$1
    local url=$2
    
    if [ -z "$url" ]; then
        echo -e "${RED}  ❌ ${name}: URL no disponible${NC}"
        return 1
    fi
    
    if curl -f -s "${url}/health" >/dev/null 2>&1; then
        echo -e "${GREEN}  ✅ ${name}: OK${NC}"
        return 0
    else
        echo -e "${YELLOW}  ⚠️  ${name}: No responde aún${NC}"
        return 1
    fi
}

check_service "Auth Service" "$AUTH_URL"
check_service "Product Service" "$PRODUCT_URL"
check_service "Order Service" "$ORDER_URL"
check_service "Logistics Service" "$LOGISTICS_URL"
check_service "Notifications Service" "$NOTIFICATIONS_URL"

echo ""

# Mostrar URLs
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Pipeline Local Completado${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "📊 URLs de Servicios:"
echo ""
[ -n "$AUTH_URL" ] && echo "  🔐 Auth Service: $AUTH_URL"
[ -n "$PRODUCT_URL" ] && echo "  📦 Product Service: $PRODUCT_URL"
[ -n "$ORDER_URL" ] && echo "  📋 Order Service: $ORDER_URL"
[ -n "$LOGISTICS_URL" ] && echo "  🚚 Logistics Service: $LOGISTICS_URL"
[ -n "$NOTIFICATIONS_URL" ] && echo "  🔔 Notifications Service: $NOTIFICATIONS_URL"
echo ""
echo -e "${GREEN}🎉 ¡Pipeline ejecutado exitosamente!${NC}"
echo ""

