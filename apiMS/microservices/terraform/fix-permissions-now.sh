#!/bin/bash

# ==============================================================================
# Script Rápido para Arreglar Permisos - Ejecutar con Variables de Entorno
# ==============================================================================
# Uso: PROJECT_ID=tu-proyecto SERVICE_ACCOUNT=sa@proyecto.iam.gserviceaccount.com ./fix-permissions-now.sh
# ==============================================================================

set -e

echo "🔧 Arreglando Permisos del Service Account"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar variables de entorno
if [ -z "$PROJECT_ID" ] || [ -z "$SERVICE_ACCOUNT" ]; then
    echo -e "${RED}❌ Error: Necesitas proporcionar PROJECT_ID y SERVICE_ACCOUNT${NC}"
    echo ""
    echo "Uso:"
    echo "  export PROJECT_ID='tu-proyecto-id'"
    echo "  export SERVICE_ACCOUNT='terraform-sa@tu-proyecto.iam.gserviceaccount.com'"
    echo "  ./fix-permissions-now.sh"
    echo ""
    exit 1
fi

echo "📋 Proyecto: $PROJECT_ID"
echo "📧 Service Account: $SERVICE_ACCOUNT"
echo ""

# Configurar proyecto
gcloud config set project $PROJECT_ID >/dev/null 2>&1

# Habilitar API si no está habilitada
echo "🔌 Habilitando API de Cloud SQL Admin..."
gcloud services enable sqladmin.googleapis.com --project=$PROJECT_ID 2>/dev/null || true

# Roles necesarios
ROLES=(
    "roles/run.admin"
    "roles/artifactregistry.admin"
    "roles/secretmanager.admin"
    "roles/iam.serviceAccountUser"
    "roles/cloudsql.admin"
    "roles/iam.securityAdmin"
)

echo ""
echo "🔐 Asignando roles necesarios..."
echo ""

# Asignar cada rol (sin redirigir errores para ver si hay problemas)
for ROLE in "${ROLES[@]}"; do
    echo -n "   Asignando $ROLE... "
    if gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SERVICE_ACCOUNT}" \
        --role="$ROLE" 2>&1; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${YELLOW}⚠️  (puede que ya esté asignado)${NC}"
    fi
done

echo ""
echo -e "${GREEN}✅ Permisos actualizados!${NC}"
echo ""
echo "⏳ Espera 1-2 minutos para que los cambios se propaguen antes de ejecutar Terraform."
echo ""

