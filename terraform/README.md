# Terraform - Despliegue de MediSupply Monolith en GCP

Esta configuración de Terraform despliega el monolito MediSupply en Google Cloud Platform usando Cloud Run.

## 📋 Requisitos Previos

1. **GCP Project**: Tener un proyecto de GCP creado
2. **Service Account**: Crear un Service Account con los siguientes roles:
   - `roles/run.admin`
   - `roles/artifactregistry.admin`
   - `roles/secretmanager.admin`
   - `roles/cloudsql.admin` (si usas Cloud SQL)
   - `roles/iam.serviceAccountUser`
   - `roles/servicemanagement.serviceController`
3. **Terraform**: Instalar Terraform >= 1.0
4. **gcloud CLI**: Instalar y configurar Google Cloud SDK

## 🚀 Configuración Inicial

### 1. Configurar variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edita `terraform.tfvars` con tus valores:

```hcl
project_id  = "tu-proyecto-gcp"
region      = "us-central1"
environment = "production"
```

### 2. Autenticar con GCP

```bash
gcloud auth application-default login
```

O usa un Service Account:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

### 3. Inicializar Terraform

```bash
terraform init
```

### 4. Revisar el plan

```bash
terraform plan
```

### 5. Aplicar cambios

```bash
terraform apply
```

## 📦 Recursos Creados

### Cloud Run
- **Service**: Servicio Cloud Run para el monolito
- **Configuración**: CPU, memoria, escalado automático
- **Health Checks**: Startup y liveness probes

### Artifact Registry
- **Repository**: Repositorio Docker para las imágenes
- **Formato**: DOCKER

### Secret Manager
- **SECRET_KEY**: Clave secreta para JWT
- **DATABASE_URL**: URL de conexión a la base de datos (si Cloud SQL está habilitado)

### Service Account
- **Cloud Run SA**: Service Account con permisos necesarios
- **IAM Bindings**: Permisos para Secret Manager y Cloud SQL

### Cloud SQL (Opcional)
- **Instance**: Instancia de PostgreSQL
- **Database**: Base de datos `medisupply`
- **User**: Usuario de base de datos

## 🔧 Variables Principales

| Variable | Descripción | Default |
|----------|-------------|---------|
| `project_id` | ID del proyecto GCP | - |
| `region` | Región de GCP | `us-central1` |
| `service_name` | Nombre del servicio Cloud Run | `medisupply-monolith` |
| `container_port` | Puerto del contenedor | `8000` |
| `cpu_limit` | Límite de CPU | `2` |
| `memory_limit` | Límite de memoria | `2Gi` |
| `min_instances` | Instancias mínimas | `0` |
| `max_instances` | Instancias máximas | `10` |
| `enable_cloud_sql` | Habilitar Cloud SQL | `false` |

## 📤 Outputs

Después de aplicar Terraform, obtendrás:

- `cloud_run_service_url`: URL del servicio desplegado
- `artifact_registry_repository_url`: URL del repositorio de imágenes
- `service_account_email`: Email del Service Account
- `cloud_sql_connection_name`: Nombre de conexión de Cloud SQL (si está habilitado)

## 🔐 Secrets

### Configurar SECRET_KEY en Secret Manager

```bash
# Crear el secret (si no existe)
gcloud secrets create medisupply-secret-key \
  --project=tu-proyecto-gcp

# Agregar el valor
echo -n "tu-secret-key-aqui" | gcloud secrets versions add medisupply-secret-key \
  --data-file=- \
  --project=tu-proyecto-gcp
```

### Configurar DATABASE_URL (si usas Cloud SQL)

```bash
# Crear el secret
gcloud secrets create medisupply-database-url \
  --project=tu-proyecto-gcp

# Agregar el valor
echo -n "postgresql://user:pass@host:5432/dbname" | gcloud secrets versions add medisupply-database-url \
  --data-file=- \
  --project=tu-proyecto-gcp
```

## 🧹 Limpieza

Para eliminar todos los recursos:

```bash
terraform destroy
```

**⚠️ Advertencia**: Esto eliminará todos los recursos creados por Terraform.

## 📝 Notas

- El servicio Cloud Run se despliega con acceso público por defecto (`allow_unauthenticated = true`)
- Para producción, considera cambiar `allow_unauthenticated = false` y usar autenticación
- Cloud SQL está deshabilitado por defecto. Para habilitarlo, configura `enable_cloud_sql = true`
- El health check endpoint debe estar disponible en `/health`

## 🔗 Enlaces Útiles

- [Documentación de Cloud Run](https://cloud.google.com/run/docs)
- [Documentación de Artifact Registry](https://cloud.google.com/artifact-registry/docs)
- [Documentación de Secret Manager](https://cloud.google.com/secret-manager/docs)
- [Documentación de Cloud SQL](https://cloud.google.com/sql/docs)

