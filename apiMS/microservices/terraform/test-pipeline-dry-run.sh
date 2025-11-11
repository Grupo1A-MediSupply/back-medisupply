#!/bin/bash

# ==============================================================================
# Script para probar el pipeline SIN aplicar cambios (Dry Run)
# ==============================================================================

set -e

cd "$(dirname "$0")"
SCRIPT_DIR=$(pwd)
cd "$SCRIPT_DIR/.."

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    🧪 Dry Run del Pipeline (Sin Aplicar Cambios)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

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
echo "🔍 Verificando herramientas..."
command -v docker >/dev/null 2>&1 || { echo "❌ Docker no está instalado"; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "❌ Terraform no está instalado"; exit 1; }
command -v gcloud >/dev/null 2>&1 || { echo "❌ gcloud no está instalado"; exit 1; }
echo "✅ Todas las herramientas están instaladas"
echo ""

# Verificar Docker
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker daemon no está corriendo"
    exit 1
fi
echo "✅ Docker está corriendo"
echo ""

# Verificar autenticación
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ No estás autenticado en GCP"
    exit 1
fi
echo "✅ Autenticado en GCP"
echo ""

# JOB 1: Build and Push (simulado)
echo -e "${BLUE}📦 JOB 1: Build and Push Docker Images${NC}"
echo "  - Verificaría Artifact Registry"
echo "  - Construiría 5 imágenes Docker"
echo "  - Subiría imágenes a Artifact Registry"
echo ""
echo -e "${YELLOW}⚠️  DRY RUN: No se construirán imágenes${NC}"
echo ""

# JOB 2: Deploy (simulado)
echo -e "${BLUE}🚀 JOB 2: Deploy with Terraform${NC}"
cd terraform

echo "  - Inicializando Terraform..."
terraform init >/dev/null 2>&1
echo "  ✅ Terraform inicializado"

echo "  - Validando configuración..."
terraform validate >/dev/null 2>&1 && echo "  ✅ Configuración válida" || echo "  ❌ Errores encontrados"

echo "  - Generando plan..."
terraform plan -out=tfplan.dry >/dev/null 2>&1
echo "  ✅ Plan generado"

echo ""
echo "📊 Resumen de cambios planificados:"
terraform show -json tfplan.dry 2>/dev/null | python3 -c "
import sys, json
plan = json.load(sys.stdin)
resources = plan.get('resource_changes', [])
creates = [r for r in resources if r['change']['actions'] == ['create']]
updates = [r for r in resources if r['change']['actions'] == ['update']]
deletes = [r for r in resources if r['change']['actions'] == ['delete']]
print(f'  Crear: {len(creates)} recursos')
print(f'  Actualizar: {len(updates)} recursos')
print(f'  Eliminar: {len(deletes)} recursos')
if creates:
    print('')
    print('  Recursos a crear:')
    for r in creates[:10]:
        print(f'    - {r[\"address\"]}')
" 2>/dev/null || terraform plan tfplan.dry 2>&1 | grep -E "(will be created|will be updated|will be destroyed)" | head -10

echo ""
echo -e "${YELLOW}⚠️  DRY RUN: No se aplicarán cambios${NC}"
echo ""

# JOB 3: Health Check (simulado)
echo -e "${BLUE}🏥 JOB 3: Health Check${NC}"
echo "  - Verificaría health endpoints de todos los servicios"
echo "  - Reportaría estado de cada servicio"
echo ""

echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Dry Run Completado${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Para ejecutar el pipeline completo, usa:"
echo "  ./test-pipeline-local.sh"
echo ""

