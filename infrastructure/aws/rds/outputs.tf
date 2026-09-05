# ============================================================
# AI Resume Screening & Interview System
# AWS RDS Outputs
# File: infrastructure/aws/rds/outputs.tf
# ============================================================


# ============================================================
# RDS INSTANCE
# ============================================================

output "db_instance_id" {
  description = "RDS PostgreSQL instance identifier"
  value       = aws_db_instance.main.id
}

output "db_instance_arn" {
  description = "RDS PostgreSQL instance ARN"
  value       = aws_db_instance.main.arn
}

output "db_instance_identifier" {
  description = "RDS PostgreSQL instance identifier"
  value       = aws_db_instance.main.identifier
}

output "db_instance_status" {
  description = "Current RDS instance status"
  value       = aws_db_instance.main.status
}


# ============================================================
# DATABASE CONNECTION
# ============================================================

output "db_endpoint" {
  description = "RDS PostgreSQL endpoint hostname"
  value       = aws_db_instance.main.address
}

output "db_address" {
  description = "RDS PostgreSQL hostname"
  value       = aws_db_instance.main.address
}

output "db_port" {
  description = "RDS PostgreSQL port"
  value       = aws_db_instance.main.port
}

output "db_name" {
  description = "Application database name"
  value       = aws_db_instance.main.db_name
}

output "db_username" {
  description = "Database master username"
  value       = aws_db_instance.main.username
  sensitive   = true
}


# ============================================================
# DATABASE URL
# ============================================================

output "database_url" {
  description = "PostgreSQL connection URL"
  value = format(
    "postgresql://%s@%s:%s/%s",
    aws_db_instance.main.username,
    aws_db_instance.main.address,
    aws_db_instance.main.port,
    aws_db_instance.main.db_name
  )
  sensitive = true
}


# ============================================================
# RDS NETWORKING
# ============================================================

output "db_subnet_group_name" {
  description = "RDS DB subnet group name"
  value       = aws_db_subnet_group.main.name
}

output "db_subnet_group_arn" {
  description = "RDS DB subnet group ARN"
  value       = aws_db_subnet_group.main.arn
}

output "db_security_group_id" {
  description = "Security group associated with RDS"
  value       = var.database_security_group_id
}


# ============================================================
# RDS CONFIGURATION
# ============================================================

output "db_engine" {
  description = "Database engine"
  value       = aws_db_instance.main.engine
}

output "db_engine_version" {
  description = "PostgreSQL engine version"
  value       = aws_db_instance.main.engine_version
}

output "db_instance_class" {
  description = "RDS instance class"
  value       = aws_db_instance.main.instance_class
}

output "db_storage_type" {
  description = "RDS storage type"
  value       = aws_db_instance.main.storage_type
}

output "db_allocated_storage" {
  description = "Allocated RDS storage in GB"
  value       = aws_db_instance.main.allocated_storage
}

output "db_max_allocated_storage" {
  description = "Maximum RDS autoscaling storage in GB"
  value       = aws_db_instance.main.max_allocated_storage
}


# ============================================================
# HIGH AVAILABILITY
# ============================================================

output "db_multi_az" {
  description = "Whether RDS Multi-AZ is enabled"
  value       = aws_db_instance.main.multi_az
}

output "db_availability_zone" {
  description = "RDS availability zone"
  value       = aws_db_instance.main.availability_zone
}

output "db_secondary_availability_zone" {
  description = "RDS secondary availability zone"
  value       = aws_db_instance.main.secondary_availability_zone
}


# ============================================================
# BACKUPS
# ============================================================

output "db_backup_retention_period" {
  description = "RDS automated backup retention period"
  value       = aws_db_instance.main.backup_retention_period
}

output "db_backup_window" {
  description = "RDS preferred backup window"
  value       = aws_db_instance.main.backup_window
}

output "db_maintenance_window" {
  description = "RDS preferred maintenance window"
  value       = aws_db_instance.main.maintenance_window
}

output "db_latest_restorable_time" {
  description = "Latest point in time to which the database can be restored"
  value       = aws_db_instance.main.latest_restorable_time
}


# ============================================================
# SECURITY
# ============================================================

output "db_storage_encrypted" {
  description = "Whether RDS storage encryption is enabled"
  value       = aws_db_instance.main.storage_encrypted
}

output "db_kms_key_id" {
  description = "KMS key used to encrypt RDS storage"
  value       = aws_db_instance.main.kms_key_id
}

output "db_publicly_accessible" {
  description = "Whether RDS is publicly accessible"
  value       = aws_db_instance.main.publicly_accessible
}

output "db_deletion_protection" {
  description = "Whether RDS deletion protection is enabled"
  value       = aws_db_instance.main.deletion_protection
}


# ============================================================
# PARAMETER GROUP
# ============================================================

output "db_parameter_group_name" {
  description = "RDS PostgreSQL parameter group name"
  value       = aws_db_parameter_group.postgres.name
}

output "db_parameter_group_arn" {
  description = "RDS PostgreSQL parameter group ARN"
  value       = aws_db_parameter_group.postgres.arn
}


# ============================================================
# OPTION GROUP
# ============================================================

output "db_option_group_name" {
  description = "RDS PostgreSQL option group name"
  value       = aws_db_option_group.postgres.name
}

output "db_option_group_arn" {
  description = "RDS PostgreSQL option group ARN"
  value       = aws_db_option_group.postgres.arn
}


# ============================================================
# SECRETS MANAGER
# ============================================================

output "database_secret_arn" {
  description = "Secrets Manager ARN containing database credentials"
  value       = aws_secretsmanager_secret.database.arn
}

output "database_secret_name" {
  description = "Secrets Manager name containing database credentials"
  value       = aws_secretsmanager_secret.database.name
}

output "database_secret_version_id" {
  description = "Current Secrets Manager secret version ID"
  value       = aws_secretsmanager_secret_version.database.version_id
}


# ============================================================
# MONITORING
# ============================================================

output "rds_monitoring_role_arn" {
  description = "IAM role ARN used by RDS Enhanced Monitoring"
  value = (
    var.monitoring_interval > 0
    ? aws_iam_role.rds_monitoring[0].arn
    : null
  )
}


# ============================================================
# RDS EVENT SUBSCRIPTION
# ============================================================

output "rds_event_subscription_arn" {
  description = "RDS event subscription ARN"
  value = (
    var.sns_topic_arn != ""
    ? aws_db_event_subscription.main[0].arn
    : null
  )
}

output "rds_event_subscription_name" {
  description = "RDS event subscription name"
  value = (
    var.sns_topic_arn != ""
    ? aws_db_event_subscription.main[0].name
    : null
  )
}