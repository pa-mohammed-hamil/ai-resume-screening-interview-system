# ============================================================
# AI Resume Screening & Interview System
# AWS S3 Variables
# File: infrastructure/aws/s3/variables.tf
# ============================================================


# ============================================================
# PROJECT
# ============================================================

variable "project_name" {
  description = "Project name used for naming AWS resources"
  type        = string
  default     = "ai-resume-screening"

  validation {
    condition     = length(var.project_name) > 0
    error_message = "project_name must not be empty."
  }
}


variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"

  validation {
    condition = contains(
      ["development", "staging", "production"],
      var.environment
    )

    error_message = "environment must be development, staging, or production."
  }
}


# ============================================================
# S3 BUCKET NAME
# ============================================================

variable "bucket_suffix" {
  description = "Globally unique suffix for S3 bucket names"
  type        = string

  validation {
    condition = can(
      regex(
        "^[a-z0-9][a-z0-9.-]{2,48}[a-z0-9]$",
        var.bucket_suffix
      )
    )

    error_message = "bucket_suffix must contain 4-50 lowercase letters, numbers, dots, or hyphens and must start/end with a letter or number."
  }
}


# ============================================================
# BUCKET DELETION
# ============================================================

variable "force_destroy" {
  description = "Allow Terraform to delete non-empty S3 buckets"
  type        = bool
  default     = false
}


# ============================================================
# VERSIONING
# ============================================================

variable "enable_versioning" {
  description = "Enable versioning on persistent S3 buckets"
  type        = bool
  default     = true
}


# ============================================================
# ENCRYPTION
# ============================================================

variable "kms_key_arn" {
  description = "Optional customer-managed KMS key ARN for S3 encryption. Empty string uses SSE-S3."
  type        = string
  default     = ""

  validation {
    condition = (
      var.kms_key_arn == "" ||
      can(regex("^arn:[^:]+:kms:[^:]+:[0-9]{12}:key/.+$", var.kms_key_arn))
    )

    error_message = "kms_key_arn must be a valid KMS key ARN or an empty string."
  }
}


# ============================================================
# CORS
# ============================================================

variable "allowed_origins" {
  description = "Frontend origins allowed to access S3 using CORS"
  type        = list(string)

  default = [
    "http://localhost:3000",
    "http://localhost:8080"
  ]

  validation {
    condition     = length(var.allowed_origins) > 0
    error_message = "At least one allowed origin must be configured."
  }
}


# ============================================================
# TEMPORARY FILE RETENTION
# ============================================================

variable "temporary_file_retention_days" {
  description = "Number of days before temporary S3 objects are automatically deleted"
  type        = number
  default     = 7

  validation {
    condition = (
      var.temporary_file_retention_days >= 1 &&
      var.temporary_file_retention_days <= 365
    )

    error_message = "temporary_file_retention_days must be between 1 and 365."
  }
}