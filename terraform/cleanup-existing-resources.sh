#!/bin/bash

# Script para limpiar recursos existentes de AWS
# ⚠️ ADVERTENCIA: Este script eliminará recursos existentes
# Uso: ./cleanup-existing-resources.sh

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

echo "⚠️  ADVERTENCIA: ESTE SCRIPT ELIMINARÁ RECURSOS EXISTENTES DE AWS"
echo "================================================================"
echo ""
echo "Este script eliminará los siguientes recursos:"
echo "- Load Balancer: medisupply-alb"
echo "- Target Group: medisupply-tg"
echo "- ECR Repositories: medisupply-auth-service, medisupply-product-service"
echo "- IAM Roles: medisupply-ecs-task-execution-role, medisupply-ecs-task-role"
echo "- CloudWatch Log Group: /ecs/medisupply"
echo "- ECS Cluster: medisupply-cluster"
echo "- ECS Service: medisupply-service"
echo ""

# Confirmar antes de proceder
read -p "¿Estás seguro de que quieres continuar? (escribe 'yes' para confirmar): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Operación cancelada."
    exit 0
fi

log "Iniciando limpieza de recursos existentes..."

# Eliminar ECS Service primero
log "Eliminando ECS Service..."
aws ecs update-service --cluster medisupply-cluster --service medisupply-service --desired-count 0 2>/dev/null || echo "ECS Service no encontrado"
aws ecs delete-service --cluster medisupply-cluster --service medisupply-service 2>/dev/null || echo "ECS Service no encontrado"

# Eliminar Load Balancer
log "Eliminando Load Balancer..."
ALB_ARN=$(aws elbv2 describe-load-balancers --names medisupply-alb --query 'LoadBalancers[0].LoadBalancerArn' --output text 2>/dev/null || echo "")
if [ "$ALB_ARN" != "" ] && [ "$ALB_ARN" != "None" ]; then
    aws elbv2 delete-load-balancer --load-balancer-arn "$ALB_ARN"
    success "Load Balancer eliminado"
else
    warning "Load Balancer no encontrado"
fi

# Eliminar Target Group
log "Eliminando Target Group..."
TG_ARN=$(aws elbv2 describe-target-groups --names medisupply-tg --query 'TargetGroups[0].TargetGroupArn' --output text 2>/dev/null || echo "")
if [ "$TG_ARN" != "" ] && [ "$TG_ARN" != "None" ]; then
    aws elbv2 delete-target-group --target-group-arn "$TG_ARN"
    success "Target Group eliminado"
else
    warning "Target Group no encontrado"
fi

# Eliminar ECR Repositories
log "Eliminando ECR Repositories..."
aws ecr delete-repository --repository-name medisupply-auth-service --force 2>/dev/null || warning "ECR auth-service no encontrado"
aws ecr delete-repository --repository-name medisupply-product-service --force 2>/dev/null || warning "ECR product-service no encontrado"

# Eliminar IAM Roles
log "Eliminando IAM Roles..."
aws iam delete-role --role-name medisupply-ecs-task-execution-role 2>/dev/null || warning "IAM role ecs_task_execution_role no encontrado"
aws iam delete-role --role-name medisupply-ecs-task-role 2>/dev/null || warning "IAM role ecs_task_role no encontrado"

# Eliminar CloudWatch Log Group
log "Eliminando CloudWatch Log Group..."
aws logs delete-log-group --log-group-name /ecs/medisupply 2>/dev/null || warning "CloudWatch Log Group no encontrado"

# Eliminar ECS Cluster
log "Eliminando ECS Cluster..."
aws ecs delete-cluster --cluster medisupply-cluster 2>/dev/null || warning "ECS Cluster no encontrado"

success "Limpieza completada. Ahora puedes ejecutar el pipeline de nuevo."
echo ""
echo "📋 Próximos pasos:"
echo "1. Ejecuta el pipeline de GitHub Actions nuevamente"
echo "2. O ejecuta 'terraform apply' localmente"
