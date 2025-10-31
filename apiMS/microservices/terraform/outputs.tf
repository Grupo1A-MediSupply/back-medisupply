# ==============================================================================
# Outputs de Terraform
# ==============================================================================

output "artifact_registry_url" {
  description = "URL del Artifact Registry"
  value       = google_artifact_registry_repository.docker_repo.name
}

output "auth_service_url" {
  description = "URL del Auth Service"
  value       = google_cloud_run_service.auth_service.status[0].url
}

output "product_service_url" {
  description = "URL del Product Service"
  value       = google_cloud_run_service.product_service.status[0].url
}

output "order_service_url" {
  description = "URL del Order Service"
  value       = google_cloud_run_service.order_service.status[0].url
}

output "logistics_service_url" {
  description = "URL del Logistics Service"
  value       = google_cloud_run_service.logistics_service.status[0].url
}

output "notifications_service_url" {
  description = "URL del Notifications Service"
  value       = google_cloud_run_service.notifications_service.status[0].url
}

output "services_info" {
  description = "Información de todos los servicios"
  value = {
    auth_service          = google_cloud_run_service.auth_service.status[0].url
    product_service       = google_cloud_run_service.product_service.status[0].url
    order_service         = google_cloud_run_service.order_service.status[0].url
    logistics_service     = google_cloud_run_service.logistics_service.status[0].url
    notifications_service = google_cloud_run_service.notifications_service.status[0].url
  }
}

output "cloud_sql_instance_name" {
  description = "Nombre de la instancia Cloud SQL"
  value       = var.enable_cloud_sql ? google_sql_database_instance.postgres[0].name : null
}

output "cloud_sql_connection_name" {
  description = "Connection name de Cloud SQL para usar en Cloud Run"
  value       = var.enable_cloud_sql ? google_sql_database_instance.postgres[0].connection_name : null
}

output "cloud_sql_databases" {
  description = "Nombres de las bases de datos creadas"
  value = var.enable_cloud_sql ? {
    auth          = google_sql_database.auth_db[0].name
    product       = google_sql_database.product_db[0].name
    order         = google_sql_database.order_db[0].name
    logistics     = google_sql_database.logistics_db[0].name
    notifications = google_sql_database.notifications_db[0].name
  } : {}
}

