# Configuración del provider GCP
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Data source para obtener información del proyecto
data "google_project" "project" {
  project_id = var.project_id
}

# Habilitar APIs necesarias
locals {
  required_apis = concat(
    [
      "run.googleapis.com",
      "artifactregistry.googleapis.com",
      "secretmanager.googleapis.com"
    ],
    var.enable_cloud_sql ? ["cloudsql.googleapis.com"] : [],
    var.create_service_account ? ["iam.googleapis.com"] : []
  )
}

resource "google_project_service" "required_apis" {
  for_each = toset(local.required_apis)

  service = each.value
  project = var.project_id

  disable_on_destroy = false
}

# Artifact Registry Repository para el monolito
# Si use_existing_artifact_registry = true, no intenta crear el repositorio
# (asume que ya existe y fue creado por el pipeline o manualmente)
resource "google_artifact_registry_repository" "monolith" {
  count         = var.use_existing_artifact_registry ? 0 : 1
  location      = var.region
  repository_id = var.artifact_registry_name
  description   = "Docker repository for MediSupply Monolith"
  format        = "DOCKER"

  depends_on = [google_project_service.required_apis]
}

# Cloud SQL Instance (PostgreSQL) - Opcional
resource "google_sql_database_instance" "main" {
  count            = var.enable_cloud_sql ? 1 : 0
  name             = "${var.project_name}-db-instance"
  database_version = var.db_version
  region           = var.region

  settings {
    tier              = var.db_tier
    availability_type = var.db_availability_type
    disk_size         = var.db_disk_size
    disk_type         = "PD_SSD"
    disk_autoresize   = true

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
    }

    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = null
      enable_private_path_for_google_cloud_services = true
    }

    database_flags {
      name  = "max_connections"
      value = "100"
    }
  }

  deletion_protection = false

  depends_on = [google_project_service.required_apis]
}

# Cloud SQL Database
resource "google_sql_database" "main" {
  count    = var.enable_cloud_sql ? 1 : 0
  name     = var.db_name
  instance = google_sql_database_instance.main[0].name
}

# Cloud SQL User
resource "google_sql_user" "main" {
  count    = var.enable_cloud_sql ? 1 : 0
  name     = var.db_user
  instance = google_sql_database_instance.main[0].name
  password = var.db_password
}

# Data source para obtener secret existente (si use_existing_secrets = true)
data "google_secret_manager_secret" "secret_key_existing" {
  count     = var.use_existing_secrets ? 1 : 0
  secret_id = "${var.project_name}-secret-key"
}

data "google_secret_manager_secret" "database_url_existing" {
  count     = var.use_existing_secrets && var.enable_cloud_sql ? 1 : 0
  secret_id = "${var.project_name}-database-url"
}

# Secret Manager para SECRET_KEY
resource "google_secret_manager_secret" "secret_key" {
  count     = var.use_existing_secrets ? 0 : 1
  secret_id = "${var.project_name}-secret-key"

  replication {
    auto {}
  }

  depends_on = [google_project_service.required_apis]
}

# Versión del secret SECRET_KEY (crear si se proporciona el valor)
# Esto funciona tanto para secrets existentes como para nuevos
# El campo 'secret' puede usar el nombre simple o el ID completo
resource "google_secret_manager_secret_version" "secret_key" {
  count       = var.secret_key != "" ? 1 : 0
  # Usar el nombre simple del secret (funciona tanto para existentes como nuevos)
  secret      = "${var.project_name}-secret-key"
  secret_data = var.secret_key

  depends_on = [
    google_secret_manager_secret.secret_key,
    data.google_secret_manager_secret.secret_key_existing,
    google_secret_manager_secret_iam_member.secret_key_accessor,
    google_project_service.required_apis
  ]
}

# Secret Manager para DATABASE_URL (si se usa Cloud SQL)
resource "google_secret_manager_secret" "database_url" {
  count     = var.enable_cloud_sql && !var.use_existing_secrets ? 1 : 0
  secret_id = "${var.project_name}-database-url"

  replication {
    auto {}
  }

  depends_on = [google_project_service.required_apis]
}

# Service Account para Cloud Run (opcional, puede usar uno existente)
resource "google_service_account" "cloud_run" {
  count        = var.create_service_account ? 1 : 0
  account_id   = "${var.project_name}-cloud-run-sa"
  display_name = "Cloud Run Service Account for MediSupply Monolith"
}

# Locals para determinar qué recursos usar (creados o existentes)
locals {
  # Secret IDs completos (para IAM y referencias): usar existentes o creados
  secret_key_id = var.use_existing_secrets ? data.google_secret_manager_secret.secret_key_existing[0].secret_id : google_secret_manager_secret.secret_key[0].secret_id
  database_url_secret_id = var.enable_cloud_sql ? (
    var.use_existing_secrets ? data.google_secret_manager_secret.database_url_existing[0].secret_id : google_secret_manager_secret.database_url[0].secret_id
  ) : null
  
  # Secret IDs simples (solo el nombre, para crear versiones)
  secret_key_id_simple = "${var.project_name}-secret-key"
  database_url_secret_id_simple = "${var.project_name}-database-url"

  # Service Account email: usar existente o creado
  # Si create_service_account = false y service_account_email está vacío,
  # intentar usar el Compute Engine default service account como fallback
  service_account_email = var.create_service_account ? google_service_account.cloud_run[0].email : (
    var.service_account_email != "" ? var.service_account_email : (
      # Fallback: usar Compute Engine default service account
      # Formato: PROJECT_NUMBER-compute@developer.gserviceaccount.com
      # Obtener el número del proyecto desde el data source
      data.google_project.project.number != null ? "${data.google_project.project.number}-compute@developer.gserviceaccount.com" : (
        # Si no podemos obtener el número, intentar crear el SA (requiere permisos)
        # Esto fallará si no hay permisos, pero es mejor que usar un SA inexistente
        "${var.project_name}-cloud-run-sa@${var.project_id}.iam.gserviceaccount.com"
      )
    )
  )
}

# IAM Binding para acceder a Secret Manager
resource "google_secret_manager_secret_iam_member" "secret_key_accessor" {
  secret_id = local.secret_key_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${local.service_account_email}"
}

resource "google_secret_manager_secret_iam_member" "database_url_accessor" {
  count     = var.enable_cloud_sql ? 1 : 0
  secret_id = local.database_url_secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${local.service_account_email}"
}

# IAM Binding para acceder a Cloud SQL (si está habilitado y el Service Account existe)
resource "google_project_iam_member" "cloud_sql_client" {
  count   = var.enable_cloud_sql && (var.create_service_account || var.service_account_email != "") ? 1 : 0
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${local.service_account_email}"
}

# Cloud Run Service
resource "google_cloud_run_v2_service" "monolith" {
  name     = var.service_name
  location = var.region

  template {
    service_account = local.service_account_email

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_name}/${var.service_name}:${var.image_tag}"

      ports {
        container_port = var.container_port
      }

      resources {
        limits = {
          cpu    = var.cpu_limit
          memory = var.memory_limit
        }
        cpu_idle = true
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "SERVICE_PORT"
        value = tostring(var.container_port)
      }

      env {
        name = "SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = local.secret_key_id
            version = "latest"
          }
        }
      }

      dynamic "env" {
        for_each = var.enable_cloud_sql ? [1] : []
        content {
          name = "DATABASE_URL"
          value_source {
            secret_key_ref {
              secret  = local.database_url_secret_id
              version = "latest"
            }
          }
        }
      }

      startup_probe {
        http_get {
          path = "/health"
        }
        initial_delay_seconds = 10
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
        }
        initial_delay_seconds = 30
        timeout_seconds       = 5
        period_seconds        = 30
        failure_threshold     = 3
      }
    }

    timeout = "300s"
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }

  depends_on = [
    google_project_service.required_apis,
    google_secret_manager_secret_version.secret_key
  ]
}

# IAM Policy para permitir acceso público (o autenticado)
resource "google_cloud_run_service_iam_member" "public_access" {
  count    = var.allow_unauthenticated ? 1 : 0
  service  = google_cloud_run_v2_service.monolith.name
  location = google_cloud_run_v2_service.monolith.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# IAM Policy para acceso autenticado (si no es público)
resource "google_cloud_run_service_iam_member" "authenticated_access" {
  count    = var.allow_unauthenticated ? 0 : 1
  service  = google_cloud_run_v2_service.monolith.name
  location = google_cloud_run_v2_service.monolith.location
  role     = "roles/run.invoker"
  member   = "allUsers" # Cambiar a "allAuthenticatedUsers" si quieres solo usuarios autenticados
}
