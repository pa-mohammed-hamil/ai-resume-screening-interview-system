# ============================================================
# AI Resume Screening & Interview System
# AWS RDS PostgreSQL Database
# File: infrastructure/aws/rds/database.tf
# ============================================================

# ============================================================
# DB SUBNET GROUP
# ============================================================

resource "aws_db_subnet_group" "main" {
  name = "${var.project_name}-${var.environment}-db-subnet-group"

  subnet_ids = var.database_subnet_ids

  description = "Private subnet group for ${var.project_name} PostgreSQL database"

  tags = {
    Name        = "${var.project_name}-${var.environment}-db-subnet-group"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# ============================================================
# RDS PARAMETER GROUP
# ============================================================

resource "aws_db_parameter_group" "postgres" {
  name        = "${var.project_name}-${var.environment}-postgres"
  family      = var.postgres_parameter_family
  description = "PostgreSQL parameter group for ${var.project_name}"

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-postgres-parameters"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# ============================================================
# RDS OPTION GROUP
# ============================================================

resource "aws_db_option_group" "postgres" {
  name                     = "${var.project_name}-${var.environment}-postgres-options"
  option_group_description = "PostgreSQL option group for ${var.project_name}"
  engine_name              = "postgres"
  major_engine_version     = var.postgres_major_version

  tags = {
    Name        = "${var.project_name}-${var.environment}-postgres-options"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# ============================================================
# RANDOM DATABASE PASSWORD
# ============================================================

resource "random_password" "database" {
  length  = 32
  special = true

  override_special = "!#$%&*()-_=+[]{}<>:?"
}


# ============================================================
# AWS SECRETS MANAGER
# ============================================================

resource "aws_secretsmanager_secret" "database" {
  name = "${var.project_name}/${var.environment}/database"

  description = "PostgreSQL credentials for ${var.project_name}"

  recovery_window_in_days = var.secret_recovery_window_days

  tags = {
    Name        = "${var.project_name}-${var.environment}-database-secret"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# ============================================================
# DATABASE SECRET VALUE
# ============================================================

resource "aws_secretsmanager_secret_version" "database" {
  secret_id = aws_secretsmanager_secret.database.id

  secret_string = jsonencode({
    username = var.database_username
    password = random_password.database.result
    engine   = "postgres"
    host     = aws_db_instance.main.address
    port     = aws_db_instance.main.port
    dbname   = var.database_name
    database = var.database_name
  })

  depends_on = [
    aws_db_instance.main
  ]
}


# ============================================================
# RDS POSTGRESQL INSTANCE
# ============================================================

resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-${var.environment}-postgres"

  engine         = "postgres"
  engine_version = var.postgres_engine_version

  instance_class = var.db_instance_class

  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = var.storage_type
  storage_encrypted     = true

  kms_key_id = var.kms_key_arn != "" ? var.kms_key_arn : null

  db_name  = var.database_name
  username = var.database_username
  password = random_password.database.result
  port     = 5432

  db_subnet_group_name = aws_db_subnet_group.main.name

  parameter_group_name = aws_db_parameter_group.postgres.name

  option_group_name = aws_db_option_group.postgres.name

  vpc_security_group_ids = [
    var.database_security_group_id
  ]

  publicly_accessible = false

  multi_az = var.multi_az

  availability_zone = var.multi_az ? null : var.availability_zone

  backup_retention_period = var.backup_retention_period

  backup_window = var.backup_window

  maintenance_window = var.maintenance_window

  copy_tags_to_snapshot = true

  delete_automated_backups = var.delete_automated_backups

  deletion_protection = var.deletion_protection

  skip_final_snapshot = var.skip_final_snapshot

  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.project_name}-${var.environment}-final-snapshot"

  auto_minor_version_upgrade = true

  apply_immediately = var.apply_immediately

  allow_major_version_upgrade = false

  performance_insights_enabled = var.performance_insights_enabled

  performance_insights_retention_period = var.performance_insights_enabled ? var.performance_insights_retention_period : null

  monitoring_interval = var.monitoring_interval

  monitoring_role_arn = var.monitoring_interval > 0 ? aws_iam_role.rds_monitoring[0].arn : null

  enabled_cloudwatch_logs_exports = [
    "postgresql",
    "upgrade"
  ]

  tags = {
    Name        = "${var.project_name}-${var.environment}-postgres"
    Project     = var.project_name
    Environment = var.environment
    Service     = "database"
    Engine      = "postgresql"
    ManagedBy   = "Terraform"
  }

  lifecycle {
    prevent_destroy = true

    ignore_changes = [
      password
    ]
  }

  depends_on = [
    aws_db_subnet_group.main,
    aws_db_parameter_group.postgres
  ]
}


# ============================================================
# RDS ENHANCED MONITORING IAM ROLE
# ============================================================

resource "aws_iam_role" "rds_monitoring" {
  count = var.monitoring_interval > 0 ? 1 : 0

  name = "${var.project_name}-${var.environment}-rds-monitoring"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-rds-monitoring"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# ============================================================
# RDS ENHANCED MONITORING POLICY
# ============================================================

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  count = var.monitoring_interval > 0 ? 1 : 0

  role = aws_iam_role.rds_monitoring[0].name

  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}


# ============================================================
# RDS INSTANCE EVENT SUBSCRIPTION
# ============================================================

resource "aws_db_event_subscription" "main" {
  count = var.sns_topic_arn != "" ? 1 : 0

  name = "${var.project_name}-${var.environment}-rds-events"

  sns_topic = var.sns_topic_arn

  source_type = "db-instance"

  source_ids = [
    aws_db_instance.main.id
  ]

  event_categories = [
    "availability",
    "configuration change",
    "failure",
    "maintenance",
    "notification",
    "recovery"
  ]

  enabled = true

  tags = {
    Name        = "${var.project_name}-${var.environment}-rds-events"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  depends_on = [
    aws_db_instance.main
  ]
}