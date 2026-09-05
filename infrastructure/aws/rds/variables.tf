# ============================================================
# AI Resume Screening & Interview System
# AWS RDS Variables
# File: infrastructure/aws/rds/variables.tf
# ============================================================


# ============================================================
# PROJECT
# ============================================================

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "ai-resume-screening"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}


# ============================================================
# NETWORK
# ============================================================

variable "vpc_id" {
  description = "VPC ID containing the RDS database"
  type        = string
}

variable "database_subnet_ids" {
  description = "Private subnet IDs used by the RDS DB subnet group"
  type        = list(string)

  validation {
    condition     = length(var.database_subnet_ids) >= 2
    error_message = "At least two private subnet IDs are required for the RDS subnet group."
  }
}


# ============================================================
# ECS SECURITY GROUPS
# ============================================================

variable "backend_security_group_id" {
  description = "Security group ID of the ECS backend service"
  type        = string
}

variable "worker_security_group_id" {
  description = "Security group ID of the ECS Celery worker"
  type        = string
}


# ============================================================
# RDS SECURITY GROUP
# ============================================================

variable "enable_admin_access" {
  description = "Enable direct PostgreSQL administrative access"
  type        = bool
  default     = false
}

variable "admin_cidr" {
  description = "CIDR block allowed to access PostgreSQL when admin access is enabled"
  type        = string
  default     = ""

  validation {
    condition = (
      !var.enable_admin_access ||
      can(cidrhost(var.admin_cidr, 0))
    )

    error_message = "admin_cidr must be a valid CIDR block when admin access is enabled."
  }
}


# ============================================================
# POSTGRESQL ENGINE
# ============================================================

variable "postgres_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "16.4"
}

variable "postgres_major_version" {
  description = "PostgreSQL major engine version"
  type        = string
  default     = "16"
}

variable "postgres_parameter_family" {
  description = "PostgreSQL parameter group family"
  type        = string
  default     = "postgres16"
}


# ============================================================
# DATABASE
# ============================================================

variable "database_name" {
  description = "Application database name"
  type        = string
  default     = "resume_ai"

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9_]{0,62}$", var.database_name))
    error_message = "database_name must start with a letter and contain only letters, numbers, and underscores."
  }
}

variable "database_username" {
  description = "RDS master database username"
  type        = string
  default     = "resume_admin"

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9_]{0,15}$", var.database_username))
    error_message = "database_username must start with a letter and contain only letters, numbers, and underscores, with a maximum of 16 characters."
  }
}


# ============================================================
# RDS INSTANCE
# ============================================================

variable "db_instance_class" {
  description = "RDS PostgreSQL instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "allocated_storage" {
  description = "Initial RDS storage size in GB"
  type        = number
  default     = 30

  validation {
    condition     = var.allocated_storage >= 20
    error_message = "allocated_storage must be at least 20 GB."
  }
}

variable "max_allocated_storage" {
  description = "Maximum RDS storage autoscaling limit in GB"
  type        = number
  default     = 100

  validation {
    condition     = var.max_allocated_storage >= var.allocated_storage
    error_message = "max_allocated_storage must be greater than or equal to allocated_storage."
  }
}

variable "storage_type" {
  description = "RDS storage type"
  type        = string
  default     = "gp3"

  validation {
    condition     = contains(["gp2", "gp3", "io1", "io2"], var.storage_type)
    error_message = "storage_type must be gp2, gp3, io1, or io2."
  }
}


# ============================================================
# RDS ENCRYPTION
# ============================================================

variable "kms_key_arn" {
  description = "KMS key ARN used to encrypt RDS storage. Empty string uses the AWS managed RDS key."
  type        = string
  default     = ""
}


# ============================================================
# HIGH AVAILABILITY
# ============================================================

variable "multi_az" {
  description = "Enable RDS Multi-AZ deployment"
  type        = bool
  default     = true
}

variable "availability_zone" {
  description = "Availability Zone used when Multi-AZ is disabled"
  type        = string
  default     = null
}


# ============================================================
# BACKUPS
# ============================================================

variable "backup_retention_period" {
  description = "Number of days automated RDS backups are retained"
  type        = number
  default     = 7

  validation {
    condition     = var.backup_retention_period >= 0 && var.backup_retention_period <= 35
    error_message = "backup_retention_period must be between 0 and 35 days."
  }
}

variable "backup_window" {
  description = "Preferred RDS backup window in UTC"
  type        = string
  default     = "18:00-19:00"
}

variable "maintenance_window" {
  description = "Preferred RDS maintenance window in UTC"
  type        = string
  default     = "sun:19:00-sun:20:00"
}

variable "delete_automated_backups" {
  description = "Delete automated backups when the RDS instance is deleted"
  type        = bool
  default     = false
}

variable "deletion_protection" {
  description = "Protect the RDS instance from accidental deletion"
  type        = bool
  default     = true
}

variable "skip_final_snapshot" {
  description = "Skip the final RDS snapshot when deleting the database"
  type        = bool
  default     = false
}


# ============================================================
# PERFORMANCE
# ============================================================

variable "performance_insights_enabled" {
  description = "Enable RDS Performance Insights"
  type        = bool
  default     = true
}

variable "performance_insights_retention_period" {
  description = "Performance Insights retention period in days"
  type        = number
  default     = 7

  validation {
    condition = contains(
      [7, 31, 62, 93, 124, 155, 186, 217, 248, 279, 310, 341, 372, 731],
      var.performance_insights_retention_period
    )
    error_message = "performance_insights_retention_period must be a supported Performance Insights retention value."
  }
}

variable "monitoring_interval" {
  description = "RDS Enhanced Monitoring interval in seconds. Set to 0 to disable."
  type        = number
  default     = 60

  validation {
    condition     = contains([0, 1, 5, 10, 15, 30, 60], var.monitoring_interval)
    error_message = "monitoring_interval must be one of 0, 1, 5, 10, 15, 30, or 60 seconds."
  }
}

variable "apply_immediately" {
  description = "Apply RDS configuration changes immediately"
  type        = bool
  default     = false
}


# ============================================================
# CLOUDWATCH / SNS
# ============================================================

variable "sns_topic_arn" {
  description = "SNS topic ARN for RDS event notifications"
  type        = string
  default     = ""
}


# ============================================================
# SECRETS MANAGER
# ============================================================

variable "secret_recovery_window_days" {
  description = "Number of days before the database secret can be permanently deleted"
  type        = number
  default     = 7

  validation {
    condition = (
      var.secret_recovery_window_days == 0 ||
      (
        var.secret_recovery_window_days >= 7 &&
        var.secret_recovery_window_days <= 30
      )
    )

    error_message = "secret_recovery_window_days must be 0 or between 7 and 30 days."
  }
}