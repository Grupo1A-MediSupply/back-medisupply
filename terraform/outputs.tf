# Outputs para información importante después del despliegue

output "cloud_run_service_url" {
  description = "URL of the Cloud Run service"
  value       = google_cloud_run_v2_service.monolith.uri
}

output "cloud_run_service_name" {
  description = "Name of the Cloud Run service"
  value       = google_cloud_run_v2_service.monolith.name
}

output "cloud_run_service_location" {
  description = "Location of the Cloud Run service"
  value       = google_cloud_run_v2_service.monolith.location
}

output "artifact_registry_repository_url" {
  description = "URL of the Artifact Registry repository"
  value       = google_artifact_registry_repository.monolith.name
}

output "artifact_registry_repository_id" {
  description = "ID of the Artifact Registry repository"
  value       = google_artifact_registry_repository.monolith.repository_id
}

output "service_account_email" {
  description = "Email of the Cloud Run service account"
  value       = google_service_account.cloud_run.email
}

output "cloud_sql_instance_name" {
  description = "Name of the Cloud SQL instance (if enabled)"
  value       = var.enable_cloud_sql ? google_sql_database_instance.main[0].name : null
}

output "cloud_sql_connection_name" {
  description = "Connection name of the Cloud SQL instance (if enabled)"
  value       = var.enable_cloud_sql ? google_sql_database_instance.main[0].connection_name : null
}

output "secret_key_secret_id" {
  description = "Secret Manager secret ID for SECRET_KEY"
  value       = google_secret_manager_secret.secret_key.secret_id
}

output "database_url_secret_id" {
  description = "Secret Manager secret ID for DATABASE_URL (if Cloud SQL enabled)"
  value       = var.enable_cloud_sql ? google_secret_manager_secret.database_url[0].secret_id : null
}
