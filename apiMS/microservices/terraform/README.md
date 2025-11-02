# 🚀 Despliegue en GCP con Terraform

Este directorio contiene la configuración de Terraform para desplegar los microservicios MediSupply en Google Cloud Platform usando servicios gratuitos o muy económicos.

## 📋 Servicios Utilizados

### ✅ Gratuitos o Muy Económicos

1. **Cloud Run** (Serverless)
   - ✅ **Gratis hasta 2 millones de requests/mes**
   - ✅ **Escala a cero** (no pagas cuando no hay tráfico)
   - ✅ Pay-per-use (solo pagas lo que consumes)
   - Costo aproximado: **$0 - $10/mes** para desarrollo/testing

2. **Artifact Registry**
   - ✅ **500 MB de almacenamiento gratuito/mes**
   - Ideal para almacenar imágenes Docker

3. **Secret Manager**
   - ✅ **Primeros 6 secrets gratuitos**
   - ✅ **10,000 operaciones/mes gratuitas**

4. **Cloud IAM**
   - ✅ Gratuito

## 💰 Estimación de Costos

Para un entorno de desarrollo/testing con tráfico bajo:

- **Cloud Run**: $0-5/mes (2M requests gratuitas)
- **Artifact Registry**: $0/mes (500MB gratuitos)
- **Secret Manager**: $0/mes (incluido en el tier gratuito)
- **Total estimado**: **$0-5/mes** 🎉

Para producción con tráfico moderado (~100K requests/mes):
- **Cloud Run**: $10-30/mes
- **Artifact Registry**: $0-2/mes
- **Total estimado**: **$10-32/mes**

## 📦 Requisitos Previos

1. **Cuenta de GCP** con proyecto activo
2. **Terraform** instalado (>= 1.0)
3. **Google Cloud SDK** instalado
4. **Docker** instalado (para construir imágenes)

## 🔧 Configuración Inicial

### 1. Crear Proyecto en GCP

```bash
# Inicia sesión en GCP
gcloud auth login

# Crea un nuevo proyecto (o usa uno existente)
gcloud projects create tu-proyecto-id --name="MediSupply"

# Configura el proyecto actual
gcloud config set project tu-proyecto-id

# Habilita las APIs necesarias
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudresourcemanager.googleapis.com
```

### 2. Configurar Autenticación

```bash
# Crea una Service Account para Terraform
gcloud iam service-accounts create terraform-sa \
  --display-name="Terraform Service Account"

# Asigna permisos necesarios
gcloud projects add-iam-policy-binding tu-proyecto-id \
  --member="serviceAccount:terraform-sa@tu-proyecto-id.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding tu-proyecto-id \
  --member="serviceAccount:terraform-sa@tu-proyecto-id.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding tu-proyecto-id \
  --member="serviceAccount:terraform-sa@tu-proyecto-id.iam.gserviceaccount.com" \
  --role="roles/secretmanager.admin"

# Crea y descarga la clave JSON
gcloud iam service-accounts keys create terraform-key.json \
  --iam-account=terraform-sa@tu-proyecto-id.iam.gserviceaccount.com
```

### 3. Configurar Variables de Terraform

```bash
# Copia el archivo de ejemplo
cp terraform.tfvars.example terraform.tfvars

# Edita terraform.tfvars con tus valores
nano terraform.tfvars
```

Configura los siguientes valores:

```hcl
project_id = "tu-proyecto-gcp-id"
region     = "us-central1"
zone       = "us-central1-a"
environment = "dev"

# Genera una secret key segura
secret_key = "$(openssl rand -hex 32)"
```

## 🚀 Despliegue

### ⚠️ IMPORTANTE: Orden de Despliegue

**Las imágenes Docker deben existir ANTES de crear los servicios Cloud Run.**

### Opción 1: Despliegue Automático (Script)

```bash
# El script verifica y construye imágenes automáticamente
./deploy.sh
```

### Opción 2: Despliegue Manual (Dos Pasos)

#### Paso 1: Construir y Subir Imágenes Docker

```bash
# Construir y subir todas las imágenes
./build-and-push-images.sh
```

#### Paso 2: Desplegar con Terraform

```bash
# Inicializar Terraform
terraform init

# Validar configuración
terraform validate

# Ver plan de ejecución
terraform plan

# Aplicar cambios (ahora las imágenes ya existen)
terraform apply
```

### Opción 3: Despliegue Incremental

Si prefieres más control:

```bash
# 1. Crear solo Artifact Registry
terraform apply -target=google_artifact_registry_repository.docker_repo

# 2. Construir y subir imágenes
./build-and-push-images.sh

# 3. Crear secretos
terraform apply -target=google_secret_manager_secret.secret_key

# 4. Desplegar todos los servicios
terraform apply
```

### Opción 4: Despliegue Automático (GitHub Actions)

El pipeline de GitHub Actions maneja todo automáticamente:
1. Construye imágenes Docker
2. Las sube a Artifact Registry
3. Despliega con Terraform

Ver: `.github/workflows/deploy-gcp.yml`

## 📊 Verificar Despliegue

```bash
# Ver URLs de los servicios
terraform output

# Probar un servicio
curl $(terraform output -raw auth_service_url)/health

# Ver logs de un servicio
gcloud run logs read auth-service --limit=50
```

## 🗑️ Destruir Infraestructura

```bash
# Eliminar todos los recursos creados
terraform destroy
```

**⚠️ ADVERTENCIA**: Esto eliminará todos los servicios y datos. Asegúrate de hacer backup si es necesario.

## 📝 Estructura de Archivos

```
terraform/
├── main.tf                 # Recursos principales
├── variables.tf            # Variables de entrada
├── outputs.tf              # Valores de salida
├── terraform.tfvars.example # Ejemplo de configuración
├── .gitignore             # Archivos ignorados por git
└── README.md              # Esta documentación
```

## 🔐 Seguridad

1. **Nunca commitees `terraform.tfvars`** (ya está en .gitignore)
2. **Usa Secret Manager** para datos sensibles
3. **Rotar secret keys** regularmente
4. **Revisa permisos IAM** regularmente

## 🐛 Troubleshooting

### Error: Image not found

**Problema**: `Error: Image 'us-central1-docker.pkg.dev/project-id/repo/auth-service:latest' not found`

**Solución**: Las imágenes Docker deben construirse y subirse ANTES de ejecutar `terraform apply`.

```bash
# Solución rápida
./build-and-push-images.sh
terraform apply
```

Para más detalles, ver: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### Error: Permission Denied
```bash
# Verifica que la Service Account tenga los permisos correctos
gcloud projects get-iam-policy tu-proyecto-id
```

### Error: API Not Enabled
```bash
# Habilita las APIs necesarias
gcloud services enable run.googleapis.com
```

### Error: Resource Already Exists
```bash
# Importa el recurso existente
terraform import google_cloud_run_service.auth_service projects/tu-proyecto-id/locations/us-central1/services/auth-service
```

## 📚 Recursos Adicionales

- [Terraform GCP Provider Docs](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Artifact Registry Pricing](https://cloud.google.com/artifact-registry/pricing)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/)

## 🎉 ¡Listo!

Una vez desplegado, tendrás tus microservicios corriendo en Cloud Run con auto-scaling, alta disponibilidad y costos mínimos.

