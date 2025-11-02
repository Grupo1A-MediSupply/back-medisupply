#!/bin/bash

# Script para importar IAM Roles existentes a Terraform
# Ejecutar desde el directorio 'terraform/'

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║            🔄 IMPORTANDO IAM ROLES EXISTENTES                ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Configurar AWS CLI (asegúrate de tener las credenciales configuradas)
AWS_REGION="us-east-1" # Ajusta a tu región
echo "Configurando AWS CLI para la región: $AWS_REGION"
export AWS_DEFAULT_REGION=$AWS_REGION

# --- IAM Roles ---
echo "Importando IAM Roles..."
ROLES=(
    "ecs_task_execution_role:medisupply-ecs-task-execution-role"
    "ecs_task_role:medisupply-ecs-task-role"
)

for role_map in "${ROLES[@]}"; do
    TF_RESOURCE=$(echo $role_map | cut -d':' -f1)
    ROLE_NAME=$(echo $role_map | cut -d':' -f2)
    echo "Intentando importar IAM Role: $ROLE_NAME"
    
    # Verificar si el role existe
    aws iam get-role --role-name $ROLE_NAME > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        terraform import aws_iam_role.$TF_RESOURCE $ROLE_NAME
        if [ $? -eq 0 ]; then
            echo "✅ IAM Role $ROLE_NAME importado exitosamente."
        else
            echo "❌ Error al importar IAM Role $ROLE_NAME."
        fi
    else
        echo "⚠️ IAM Role $ROLE_NAME no encontrado o no necesita importación."
    fi
done

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║            ✅ IMPORTACIÓN DE IAM ROLES FINALIZADA            ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo "Ahora puedes ejecutar 'terraform plan' para verificar el estado."
