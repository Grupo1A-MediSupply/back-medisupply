#!/bin/bash
# Script para asignar roles al Compute Engine default Service Account
# Reemplaza PROJECT_ID con tu ID de proyecto GCP

set -e

PROJECT_ID="${GCP_PROJECT_ID:-tu-proyecto-id}"

if [ "$PROJECT_ID" = "tu-proyecto-id" ]; then
  echo "❌ ERROR: Debes configurar PROJECT_ID"
  echo "   Opción 1: export GCP_PROJECT_ID=tu-proyecto-id"
  echo "   Opción 2: Editar este script y cambiar PROJECT_ID"
  exit 1
fi

echo "🔐 Asignando roles al Compute Engine default SA..."
echo "   Project ID: $PROJECT_ID"
echo "   Service Account: ${PROJECT_ID}@appspot.gserviceaccount.com"
echo ""

# 1. Secret Manager (OBLIGATORIO para todos los casos)
echo "📦 Asignando roles/secretmanager.secretAccessor..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --condition=None || {
    echo "⚠️  Error al asignar roles/secretmanager.secretAccessor"
    echo "   Verifica que tengas permisos y que el SA exista"
    exit 1
  }

echo "✅ roles/secretmanager.secretAccessor asignado correctamente"
echo ""

# 2. Cloud SQL (SOLO si usas Cloud SQL)
# Descomenta las siguientes líneas si ENABLE_CLOUD_SQL = 'true'
if [ "${ENABLE_CLOUD_SQL:-false}" = "true" ]; then
  echo "🗄️  Asignando roles/cloudsql.client (Cloud SQL habilitado)..."
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
    --role="roles/cloudsql.client" \
    --condition=None || {
      echo "⚠️  Error al asignar roles/cloudsql.client"
      echo "   Verifica que tengas permisos y que Cloud SQL esté habilitado"
      exit 1
    }
  echo "✅ roles/cloudsql.client asignado correctamente"
else
  echo "⏭️  Omitiendo roles/cloudsql.client (ENABLE_CLOUD_SQL = false)"
fi

echo ""
echo "✅ Todos los roles asignados correctamente"
echo ""
echo "📋 Resumen:"
echo "   Service Account: ${PROJECT_ID}@appspot.gserviceaccount.com"
echo "   Roles asignados:"
echo "     - roles/secretmanager.secretAccessor ✅"
if [ "${ENABLE_CLOUD_SQL:-false}" = "true" ]; then
  echo "     - roles/cloudsql.client ✅"
fi

