# ============================================================
# AI Resume Screening & Interview System
# AWS RDS Security Group
# File: infrastructure/aws/rds/security-group.tf
# ============================================================

# ============================================================
# RDS SECURITY GROUP
# ============================================================

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Security group for PostgreSQL RDS"
  vpc_id      = var.vpc_id

  tags = {
    Name        = "${var.project_name}-${var.environment}-rds-sg"
    Project     = var.project_name
    Environment = var.environment
    Service     = "rds"
    ManagedBy   = "Terraform"
  }
}


# ============================================================
# POSTGRESQL ACCESS FROM BACKEND
# ============================================================

resource "aws_vpc_security_group_ingress_rule" "rds_from_backend" {
  security_group_id = aws_security_group.rds.id

  referenced_security_group_id = var.backend_security_group_id

  ip_protocol = "tcp"
  from_port   = 5432
  to_port     = 5432

  description = "Allow PostgreSQL access from ECS backend"
}


# ============================================================
# POSTGRESQL ACCESS FROM CELERY WORKER
# ============================================================

resource "aws_vpc_security_group_ingress_rule" "rds_from_worker" {
  security_group_id = aws_security_group.rds.id

  referenced_security_group_id = var.worker_security_group_id

  ip_protocol = "tcp"
  from_port   = 5432
  to_port     = 5432

  description = "Allow PostgreSQL access from ECS Celery worker"
}


# ============================================================
# OPTIONAL ADMIN ACCESS
# ============================================================
#
# Keep this disabled by default.
#
# If database administration is required, preferably connect
# through AWS Systems Manager / bastion / VPN rather than
# exposing PostgreSQL to the public internet.
#

resource "aws_vpc_security_group_ingress_rule" "rds_from_admin" {
  count = var.enable_admin_access ? 1 : 0

  security_group_id = aws_security_group.rds.id

  cidr_ipv4 = var.admin_cidr

  ip_protocol = "tcp"
  from_port   = 5432
  to_port     = 5432

  description = "Temporary PostgreSQL administrative access"
}


# ============================================================
# RDS EGRESS
# ============================================================

resource "aws_vpc_security_group_egress_rule" "rds_all_outbound" {
  security_group_id = aws_security_group.rds.id

  ip_protocol = "-1"

  cidr_ipv4 = "0.0.0.0/0"

  description = "Allow outbound traffic from RDS"
}