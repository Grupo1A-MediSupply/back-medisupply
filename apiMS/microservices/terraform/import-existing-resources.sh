#!/bin/bash

# Script para importar recursos existentes en Terraform
# Usa este script si obtienes errores 409 (recurso ya existe)

set -e

PROJECT_ID=${1:-$(gcloud config get-value project 2>/dev/null)}
REGION=${2:-"us-central1"}

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: Proporciona PROJECT_ID como argumento"
    echo "Uso: $0 PROJECT_ID [REGION]"
    exit 1
fi

echo "═══════════════════════════════════════════════════════════"
echo "     📥 IMPORTANDO RECURSOS EXISTENTES EN TERRAFORM"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📋 Proyecto: $PROJECT_ID"
echo "📍 Región: $REGION"
echo ""

# Importar Artifact Registry
REPO_ID="${PROJECT_ID}-docker-repo"
if gcloud artifacts repositories describe "$REPO_ID" --location="$REGION" --project="$PROJECT_ID" &>/dev/null; then
    echo "📦 Importando Artifact Registry: $REPO_ID"
    terraform import \
      "google_artifact_registry_repository.docker_repo" \
      "projects/$PROJECT_ID/locations/$REGION/repositories/$REPO_ID" || \
      echo "   ⚠️  Ya importado o error"
    echo ""
fi

# Importar Secret Manager
SECRET_ID="auth-service-secret-key"
if gcloud secrets describe "$SECRET_ID" --project="$PROJECT_ID" &>/dev/null; then
    echo "🔐 Importando Secret Manager: $SECRET_ID"
    terraform import \
      "google_secret_manager_secret.secret_key" \
      "projects/$PROJECT_ID/secrets/$SECRET_ID" || \
      echo "   ⚠️  Ya importado o error"
    echo ""
fi

echo "✅ Importación completada"
echo ""
echo "💡 Siguiente paso: terraform plan para verificar"
