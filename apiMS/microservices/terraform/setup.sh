#!/bin/bash

# ==============================================================================
# Script de Configuración Inicial para GCP
# ==============================================================================
# Este script configura el proyecto GCP y habilita las APIs necesarias
# ==============================================================================

set -e

echo "🚀 Configuración Inicial de GCP para MediSupply"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: Google Cloud SDK no está instalado${NC}"
    echo "Instala desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Solicitar proyecto ID
read -p "📋 Ingresa el ID de tu proyecto GCP: " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Error: Project ID es requerido${NC}"
    exit 1
fi

echo ""
echo "🔧 Configurando proyecto: $PROJECT_ID"

# Configurar proyecto
gcloud config set project $PROJECT_ID

# Verificar que el proyecto existe
if ! gcloud projects describe $PROJECT_ID &> /dev/null; then
    echo -e "${YELLOW}⚠️  El proyecto no existe. Creándolo...${NC}"
    gcloud projects create $PROJECT_ID
fi

# Habilita facturación (opcional - necesario para servicios pagos)
echo ""
echo "💳 ¿Tienes facturación habilitada? (y/n)"
read -p "> " HAS_BILLING

if [ "$HAS_BILLING" = "y" ]; then
    read -p "💳 Ingresa el Billing Account ID: " BILLING_ACCOUNT
    gcloud billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT
fi

# Habilitar APIs necesarias
echo ""
echo "🔌 Habilitando APIs necesarias..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudresourcemanager.googleapis.com \
  --project=$PROJECT_ID

echo -e "${GREEN}✅ APIs habilitadas${NC}"

# Crear Service Account para Terraform
echo ""
echo "👤 Creando Service Account para Terraform..."
gcloud iam service-accounts create terraform-sa \
  --display-name="Terraform Service Account" \
  --project=$PROJECT_ID

# Asignar roles necesarios
echo ""
echo "🔐 Asignando permisos..."

SERVICE_ACCOUNT="terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/iam.serviceAccountUser"

echo -e "${GREEN}✅ Permisos asignados${NC}"

# Crear clave JSON
echo ""
echo "🔑 Creando clave JSON para Service Account..."
gcloud iam service-accounts keys create terraform-key.json \
  --iam-account=$SERVICE_ACCOUNT \
  --project=$PROJECT_ID

echo -e "${GREEN}✅ Clave creada en: terraform-key.json${NC}"
echo -e "${YELLOW}⚠️  IMPORTANTE: Agrega este archivo a .gitignore y guárdalo de forma segura${NC}"

# Generar secret key
echo ""
echo "🔐 Generando secret key para JWT..."
SECRET_KEY=$(openssl rand -hex 32)
echo "Secret Key generada: $SECRET_KEY"
echo ""
echo -e "${YELLOW}⚠️  Guarda esta clave de forma segura. La necesitarás para terraform.tfvars${NC}"

# Configurar terraform.tfvars
echo ""
read -p "¿Quieres crear terraform.tfvars automáticamente? (y/n): " CREATE_TFVARS

if [ "$CREATE_TFVARS" = "y" ]; then
    cat > terraform.tfvars <<EOF
project_id = "$PROJECT_ID"
region     = "us-central1"
zone       = "us-central1-a"
environment = "dev"
secret_key = "$SECRET_KEY"
min_instances = 0
max_instances = 10
cpu_limit     = "1"
memory_limit  = "512Mi"
EOF
    echo -e "${GREEN}✅ terraform.tfvars creado${NC}"
fi

# Configurar autenticación para GitHub Actions
echo ""
echo "📋 Para GitHub Actions, necesitas agregar estos secrets:"
echo ""
echo "GCP_PROJECT_ID=$PROJECT_ID"
echo "GCP_REGION=us-central1"
echo "GCP_SA_KEY=(contenido de terraform-key.json)"
echo "SECRET_KEY=$SECRET_KEY"
echo ""
echo "Agrega estos valores en: Settings > Secrets > Actions"

echo ""
echo -e "${GREEN}✅ Configuración completada!${NC}"
echo ""
echo "Próximos pasos:"
echo "1. Configura terraform.tfvars (si no lo hiciste automáticamente)"
echo "2. Ejecuta: terraform init"
echo "3. Ejecuta: terraform plan"
echo "4. Ejecuta: terraform apply"
echo ""

