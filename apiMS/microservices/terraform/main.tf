# ==============================================================================
# Terraform Configuration para GCP - Microservicios MediSupply
# ==============================================================================
# Este archivo crea la infraestructura necesaria en GCP usando servicios
# gratuitos o muy económicos (Cloud Run, Artifact Registry, etc.)
# ==============================================================================

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }

  # Backend opcional: descomentar si quieres usar Cloud Storage como backend
  # backend "gcs" {
  #   bucket = "medisupply-terraform-state"
  #   prefix = "terraform/state"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# ==============================================================================
# ARTIFACT REGISTRY - Almacenamiento de imágenes Docker
# ==============================================================================

resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = "${var.project_id}-docker-repo"
  description   = "Repositorio Docker para microservicios MediSupply"
  format        = "DOCKER"
}

# ==============================================================================
# VERIFICACIÓN DE IMÁGENES - Asegurar que las imágenes existan antes de desplegar
# ==============================================================================

# Usar null_resource para verificar que Artifact Registry esté listo
resource "null_resource" "wait_for_registry" {
  depends_on = [google_artifact_registry_repository.docker_repo]
  
  triggers = {
    registry_id = google_artifact_registry_repository.docker_repo.repository_id
  }
}

# ==============================================================================
# LOCALS - Variables locales para construir URLs de conexión
# ==============================================================================

locals {
  # Connection name de Cloud SQL (si está habilitado)
  cloud_sql_connection_name = var.enable_cloud_sql ? google_sql_database_instance.postgres[0].connection_name : ""
  
  # URLs de conexión a bases de datos (codificar contraseñas para URL)
  auth_db_url = var.enable_cloud_sql ? (
    "postgresql://${google_sql_user.auth_db_user[0].name}:${urlencode(random_password.auth_db_password[0].result)}@/${google_sql_database.auth_db[0].name}?host=/cloudsql/${local.cloud_sql_connection_name}"
  ) : "sqlite:///./data/auth_service.db"
  
  product_db_url = var.enable_cloud_sql ? (
    "postgresql://${google_sql_user.product_db_user[0].name}:${urlencode(random_password.product_db_password[0].result)}@/${google_sql_database.product_db[0].name}?host=/cloudsql/${local.cloud_sql_connection_name}"
  ) : "sqlite:///./data/product_service.db"
  
  order_db_url = var.enable_cloud_sql ? (
    "postgresql://${google_sql_user.order_db_user[0].name}:${urlencode(random_password.order_db_password[0].result)}@/${google_sql_database.order_db[0].name}?host=/cloudsql/${local.cloud_sql_connection_name}"
  ) : "sqlite:///./data/order_service.db"
  
  logistics_db_url = var.enable_cloud_sql ? (
    "postgresql://${google_sql_user.logistics_db_user[0].name}:${urlencode(random_password.logistics_db_password[0].result)}@/${google_sql_database.logistics_db[0].name}?host=/cloudsql/${local.cloud_sql_connection_name}"
  ) : "sqlite:///./data/logistics_service.db"
  
  notifications_db_url = var.enable_cloud_sql ? (
    "postgresql://${google_sql_user.notifications_db_user[0].name}:${urlencode(random_password.notifications_db_password[0].result)}@/${google_sql_database.notifications_db[0].name}?host=/cloudsql/${local.cloud_sql_connection_name}"
  ) : "sqlite:///./data/notifications_service.db"
  
}

# ==============================================================================
# CLOUD RUN SERVICES - Microservicios serverless
# ==============================================================================

# Auth Service
resource "google_cloud_run_service" "auth_service" {
  name     = "auth-service"
  location = var.region

  # Las dependencias se detectan automáticamente a través de las referencias en locals
  depends_on = [null_resource.wait_for_registry]

  template {
    spec {
      containers {
        # Usar el tag específico o latest según disponibilidad
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/auth-service:latest"

        ports {
          container_port = 8001
        }

        env {
          name  = "ENVIRONMENT"
          value = "production"
        }
        env {
          name  = "DEBUG"
          value = "false"
        }
        env {
          name  = "AUTH_SERVICE_PORT"
          value = "8001"
        }
        env {
          name = "SECRET_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.secret_key.secret_id
              key  = "latest"
            }
          }
        }
        env {
          name  = "AUTH_DATABASE_URL"
          value = local.auth_db_url
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
        }
      }

      container_concurrency = 80
      timeout_seconds       = 300
    }

    metadata {
      annotations = merge({
        "autoscaling.knative.dev/minScale"  = "0"
        "autoscaling.knative.dev/maxScale"  = "10"
        "run.googleapis.com/cpu-throttling" = "true"
      }, var.enable_cloud_sql ? {
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.postgres[0].connection_name
      } : {})
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Product Service
resource "google_cloud_run_service" "product_service" {
  name     = "product-service"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/product-service:latest"

        ports {
          container_port = 8002
        }

        env {
          name  = "ENVIRONMENT"
          value = "production"
        }
        env {
          name  = "DEBUG"
          value = "false"
        }
        env {
          name  = "PRODUCT_SERVICE_PORT"
          value = "8002"
        }
        env {
          name  = "PRODUCT_DATABASE_URL"
          value = local.product_db_url
        }
        env {
          name  = "AUTH_SERVICE_URL"
          value = google_cloud_run_service.auth_service.status[0].url
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
        }
      }

      container_concurrency = 80
      timeout_seconds       = 300
    }

    metadata {
      annotations = merge({
        "autoscaling.knative.dev/minScale"  = "0"
        "autoscaling.knative.dev/maxScale"  = "10"
        "run.googleapis.com/cpu-throttling" = "true"
      }, var.enable_cloud_sql ? {
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.postgres[0].connection_name
      } : {})
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Order Service
resource "google_cloud_run_service" "order_service" {
  name     = "order-service"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/order-service:latest"

        ports {
          container_port = 8003
        }

        env {
          name  = "ENVIRONMENT"
          value = "production"
        }
        env {
          name  = "DEBUG"
          value = "false"
        }
        env {
          name  = "ORDER_SERVICE_PORT"
          value = "8003"
        }
        env {
          name  = "ORDER_DATABASE_URL"
          value = local.order_db_url
        }
        env {
          name  = "PRODUCT_SERVICE_URL"
          value = google_cloud_run_service.product_service.status[0].url
        }
        env {
          name  = "AUTH_SERVICE_URL"
          value = google_cloud_run_service.auth_service.status[0].url
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
        }
      }

      container_concurrency = 80
      timeout_seconds       = 300
    }

    metadata {
      annotations = merge({
        "autoscaling.knative.dev/minScale"  = "0"
        "autoscaling.knative.dev/maxScale"  = "10"
        "run.googleapis.com/cpu-throttling" = "true"
      }, var.enable_cloud_sql ? {
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.postgres[0].connection_name
      } : {})
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Logistics Service
resource "google_cloud_run_service" "logistics_service" {
  name     = "logistics-service"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/logistics-service:latest"

        ports {
          container_port = 8004
        }

        env {
          name  = "ENVIRONMENT"
          value = "production"
        }
        env {
          name  = "DEBUG"
          value = "false"
        }
        env {
          name  = "LOGISTICS_SERVICE_PORT"
          value = "8004"
        }
        env {
          name  = "LOGISTICS_DATABASE_URL"
          value = local.logistics_db_url
        }
        env {
          name  = "ORDER_SERVICE_URL"
          value = google_cloud_run_service.order_service.status[0].url
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
        }
      }

      container_concurrency = 80
      timeout_seconds       = 300
    }

    metadata {
      annotations = merge({
        "autoscaling.knative.dev/minScale"  = "0"
        "autoscaling.knative.dev/maxScale"  = "10"
        "run.googleapis.com/cpu-throttling" = "true"
      }, var.enable_cloud_sql ? {
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.postgres[0].connection_name
      } : {})
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Notifications Service
resource "google_cloud_run_service" "notifications_service" {
  name     = "notifications-service"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/notifications-service:latest"

        ports {
          container_port = 8007
        }

        env {
          name  = "ENVIRONMENT"
          value = "production"
        }
        env {
          name  = "DEBUG"
          value = "false"
        }
        env {
          name  = "NOTIFICATIONS_SERVICE_PORT"
          value = "8007"
        }
        env {
          name  = "NOTIFICATIONS_DATABASE_URL"
          value = local.notifications_db_url
        }
        env {
          name  = "AUTH_SERVICE_URL"
          value = google_cloud_run_service.auth_service.status[0].url
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
        }
      }

      container_concurrency = 80
      timeout_seconds       = 300
    }

    metadata {
      annotations = merge({
        "autoscaling.knative.dev/minScale"  = "0"
        "autoscaling.knative.dev/maxScale"  = "10"
        "run.googleapis.com/cpu-throttling" = "true"
      }, var.enable_cloud_sql ? {
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.postgres[0].connection_name
      } : {})
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# ==============================================================================
# IAM - Permisos para Cloud Run (público invocable)
# ==============================================================================

resource "google_cloud_run_service_iam_member" "auth_service_public" {
  service  = google_cloud_run_service.auth_service.name
  location = google_cloud_run_service.auth_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "product_service_public" {
  service  = google_cloud_run_service.product_service.name
  location = google_cloud_run_service.product_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "order_service_public" {
  service  = google_cloud_run_service.order_service.name
  location = google_cloud_run_service.order_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "logistics_service_public" {
  service  = google_cloud_run_service.logistics_service.name
  location = google_cloud_run_service.logistics_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "notifications_service_public" {
  service  = google_cloud_run_service.notifications_service.name
  location = google_cloud_run_service.notifications_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ==============================================================================
# SECRET MANAGER - Almacenamiento seguro de secretos
# ==============================================================================

resource "google_secret_manager_secret" "secret_key" {
  secret_id = "auth-service-secret-key"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "secret_key" {
  secret      = google_secret_manager_secret.secret_key.id
  secret_data = var.secret_key
}

# ==============================================================================
# CLOUD SQL - Base de datos PostgreSQL gestionada
# ==============================================================================

# Instancia de Cloud SQL PostgreSQL
resource "google_sql_database_instance" "postgres" {
  count            = var.enable_cloud_sql ? 1 : 0
  name             = "${var.project_id}-postgres-instance"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = var.db_tier

    # Configuración de disco
    disk_type       = "PD_SSD"
    disk_size       = 20 # GB mínimo (más económico)
    disk_autoresize = true

    # Configuración de backups (opcional, agregar si se necesita)
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = false
    }

    # Configuración de IP
    ip_configuration {
      ipv4_enabled    = false # No necesitamos IP pública para Cloud Run
      private_network = null
      require_ssl     = false # Cloud Run usa conexión privada
    }

    # Configuración de flags de PostgreSQL
    database_flags {
      name  = "max_connections"
      value = "100" # Suficiente para tier pequeño
    }
  }

  deletion_protection = false # Cambiar a true en producción
}

# Bases de datos para cada servicio
resource "google_sql_database" "auth_db" {
  count    = var.enable_cloud_sql ? 1 : 0
  name     = "auth_service"
  instance = google_sql_database_instance.postgres[0].name
}

resource "google_sql_database" "product_db" {
  count    = var.enable_cloud_sql ? 1 : 0
  name     = "product_service"
  instance = google_sql_database_instance.postgres[0].name
}

resource "google_sql_database" "order_db" {
  count    = var.enable_cloud_sql ? 1 : 0
  name     = "order_service"
  instance = google_sql_database_instance.postgres[0].name
}

resource "google_sql_database" "logistics_db" {
  count    = var.enable_cloud_sql ? 1 : 0
  name     = "logistics_service"
  instance = google_sql_database_instance.postgres[0].name
}

resource "google_sql_database" "notifications_db" {
  count    = var.enable_cloud_sql ? 1 : 0
  name     = "notifications_service"
  instance = google_sql_database_instance.postgres[0].name
}

# Usuario root (si se proporciona contraseña)
resource "google_sql_user" "root_user" {
  count    = var.enable_cloud_sql && var.db_root_password != "" ? 1 : 0
  name     = "postgres"
  instance = google_sql_database_instance.postgres[0].name
  password = var.db_root_password
}

# Usuarios para cada servicio (con contraseñas en Secret Manager)
resource "random_password" "auth_db_password" {
  count   = var.enable_cloud_sql ? 1 : 0
  length  = 32
  special = true
}

resource "random_password" "product_db_password" {
  count   = var.enable_cloud_sql ? 1 : 0
  length  = 32
  special = true
}

resource "random_password" "order_db_password" {
  count   = var.enable_cloud_sql ? 1 : 0
  length  = 32
  special = true
}

resource "random_password" "logistics_db_password" {
  count   = var.enable_cloud_sql ? 1 : 0
  length  = 32
  special = true
}

resource "random_password" "notifications_db_password" {
  count   = var.enable_cloud_sql ? 1 : 0
  length  = 32
  special = true
}

resource "google_sql_user" "auth_db_user" {
  count    = var.enable_cloud_sql ? 1 : 0
  name     = "auth_service_user"
  instance = google_sql_database_instance.postgres[0].name
  password = random_password.auth_db_password[0].result
}

resource "google_sql_user" "product_db_user" {
  count    = var.enable_cloud_sql ? 1 : 0
  name     = "product_service_user"
  instance = google_sql_database_instance.postgres[0].name
  password = random_password.product_db_password[0].result
}

resource "google_sql_user" "order_db_user" {
  count    = var.enable_cloud_sql ? 1 : 0
  name     = "order_service_user"
  instance = google_sql_database_instance.postgres[0].name
  password = random_password.order_db_password[0].result
}

resource "google_sql_user" "logistics_db_user" {
  count    = var.enable_cloud_sql ? 1 : 0
  name     = "logistics_service_user"
  instance = google_sql_database_instance.postgres[0].name
  password = random_password.logistics_db_password[0].result
}

resource "google_sql_user" "notifications_db_user" {
  count    = var.enable_cloud_sql ? 1 : 0
  name     = "notifications_service_user"
  instance = google_sql_database_instance.postgres[0].name
  password = random_password.notifications_db_password[0].result
}

# ==============================================================================
# SECRET MANAGER - Contraseñas de bases de datos
# ==============================================================================

resource "google_secret_manager_secret" "auth_db_password" {
  count    = var.enable_cloud_sql ? 1 : 0
  secret_id = "auth-service-db-password"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "auth_db_password" {
  count       = var.enable_cloud_sql ? 1 : 0
  secret      = google_secret_manager_secret.auth_db_password[0].id
  secret_data = random_password.auth_db_password[0].result
}

resource "google_secret_manager_secret" "product_db_password" {
  count     = var.enable_cloud_sql ? 1 : 0
  secret_id = "product-service-db-password"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "product_db_password" {
  count       = var.enable_cloud_sql ? 1 : 0
  secret      = google_secret_manager_secret.product_db_password[0].id
  secret_data = random_password.product_db_password[0].result
}

resource "google_secret_manager_secret" "order_db_password" {
  count     = var.enable_cloud_sql ? 1 : 0
  secret_id = "order-service-db-password"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "order_db_password" {
  count       = var.enable_cloud_sql ? 1 : 0
  secret      = google_secret_manager_secret.order_db_password[0].id
  secret_data = random_password.order_db_password[0].result
}

resource "google_secret_manager_secret" "logistics_db_password" {
  count     = var.enable_cloud_sql ? 1 : 0
  secret_id = "logistics-service-db-password"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "logistics_db_password" {
  count       = var.enable_cloud_sql ? 1 : 0
  secret      = google_secret_manager_secret.logistics_db_password[0].id
  secret_data = random_password.logistics_db_password[0].result
}

resource "google_secret_manager_secret" "notifications_db_password" {
  count     = var.enable_cloud_sql ? 1 : 0
  secret_id = "notifications-service-db-password"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "notifications_db_password" {
  count       = var.enable_cloud_sql ? 1 : 0
  secret      = google_secret_manager_secret.notifications_db_password[0].id
  secret_data = random_password.notifications_db_password[0].result
}

# ==============================================================================
# IAM - Permisos para Cloud Run acceder a Secret Manager
# ==============================================================================

data "google_project" "project" {
  project_id = var.project_id
}

# Permitir que Cloud Run acceda a Secret Manager
resource "google_project_iam_member" "cloud_run_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}

# Permitir que Cloud Run se conecte a Cloud SQL
resource "google_project_iam_member" "cloud_run_sql_client" {
  count   = var.enable_cloud_sql ? 1 : 0
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}

