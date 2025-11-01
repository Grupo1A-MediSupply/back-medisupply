#!/bin/bash

# ==============================================================================
# Script para Actualizar Permisos del Service Account en GCP
# ==============================================================================
# Este script actualiza los permisos del Service Account existente
# para incluir los roles necesarios para Cloud SQL e IAM
# ==============================================================================

set -e

echo "🔧 Actualización de Permisos del Service Account en GCP"
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

# Configurar proyecto
gcloud config set project $PROJECT_ID

# Solicitar Service Account email
echo ""
read -p "📧 Ingresa el email del Service Account (ej: terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com): " SERVICE_ACCOUNT_EMAIL

if [ -z "$SERVICE_ACCOUNT_EMAIL" ]; then
    echo -e "${RED}❌ Error: Service Account email es requerido${NC}"
    exit 1
fi

# Verificar que el Service Account existe
if ! gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" --project="$PROJECT_ID" &> /dev/null; then
    echo -e "${RED}❌ Error: Service Account '$SERVICE_ACCOUNT_EMAIL' no existe${NC}"
    exit 1
fi

echo ""
echo "🔌 Habilitando API de Cloud SQL Admin (si no está habilitada)..."
gcloud services enable sqladmin.googleapis.com --project=$PROJECT_ID 2>/dev/null || echo "   ✅ API ya estaba habilitada"

echo ""
echo "🔐 Actualizando permisos del Service Account: $SERVICE_ACCOUNT_EMAIL"
echo ""

# Lista de roles a asignar
ROLES=(
    "roles/run.admin"
    "roles/artifactregistry.admin"
    "roles/secretmanager.admin"
    "roles/iam.serviceAccountUser"
    "roles/cloudsql.admin"
    "roles/iam.securityAdmin"
)

# Asignar cada rol
for ROLE in "${ROLES[@]}"; do
    echo "   Asignando rol: $ROLE"
    if gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="$ROLE" 2>/dev/null; then
        echo -e "      ${GREEN}✅ Rol asignado${NC}"
    else
        echo -e "      ${YELLOW}⚠️  El rol ya estaba asignado o hubo un error${NC}"
    fi
done

echo ""
echo -e "${GREEN}✅ Actualización de permisos completada!${NC}"
echo ""
echo "📋 Verificando permisos actuales del Service Account..."
echo ""

# Verificar permisos actuales
CURRENT_ROLES=$(gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --format="value(bindings.role)" \
  --filter="bindings.members:serviceAccount:${SERVICE_ACCOUNT_EMAIL}" 2>/dev/null || echo "")

echo "📊 Roles actuales del Service Account:"
if [ -z "$CURRENT_ROLES" ]; then
    echo -e "   ${YELLOW}⚠️  No se pudieron verificar los roles actuales${NC}"
else
    echo "$CURRENT_ROLES" | while read -r role; do
        echo "   ✅ $role"
    done
fi

echo ""
echo "📋 Roles que debería tener:"
for ROLE in "${ROLES[@]}"; do
    if echo "$CURRENT_ROLES" | grep -q "^$ROLE$" 2>/dev/null; then
        echo -e "   ${GREEN}✅ $ROLE${NC} (asignado)"
    else
        echo -e "   ${RED}❌ $ROLE${NC} (faltante)"
    fi
done

echo ""
echo "💡 Si este Service Account se usa en GitHub Actions, espera 1-2 minutos para que los cambios se propaguen."
echo "   Luego ejecuta nuevamente el workflow."
echo ""

