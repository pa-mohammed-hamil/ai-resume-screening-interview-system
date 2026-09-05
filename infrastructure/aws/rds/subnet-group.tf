# ============================================================
# AI Resume Screening & Interview System
# AWS RDS Subnet Group
# File: infrastructure/aws/rds/subnet-group.tf
# ============================================================

# ============================================================
# RDS DB SUBNET GROUP
# ============================================================

resource "aws_db_subnet_group" "main" {
  name = "${var.project_name}-${var.environment}-db-subnet-group"

  description = "Private subnet group for ${var.project_name} PostgreSQL RDS"

  subnet_ids = var.database_subnet_ids

  tags = {
    Name        = "${var.project_name}-${var.environment}-db-subnet-group"
    Project     = var.project_name
    Environment = var.environment
    Service     = "rds"
    ManagedBy   = "Terraform"
  }
}