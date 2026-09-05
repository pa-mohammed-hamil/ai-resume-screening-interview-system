# ============================================================
# AI Resume Screening & Interview System
# AWS ECS Outputs
# File: infrastructure/aws/ecs/outputs.tf
# ============================================================

# ============================================================
# ECS CLUSTER
# ============================================================

output "ecs_cluster_id" {
  description = "ECS cluster ID"
  value       = aws_ecs_cluster.main.id
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  description = "ECS cluster ARN"
  value       = aws_ecs_cluster.main.arn
}

# ============================================================
# ECS CAPACITY PROVIDERS
# ============================================================

output "ecs_capacity_providers" {
  description = "ECS cluster capacity providers"
  value       = aws_ecs_cluster_capacity_providers.main.capacity_providers
}

# ============================================================
# ECS EXECUTION ROLE
# ============================================================

output "ecs_execution_role_id" {
  description = "ECS task execution IAM role ID"
  value       = aws_iam_role.ecs_execution.id
}

output "ecs_execution_role_name" {
  description = "ECS task execution IAM role name"
  value       = aws_iam_role.ecs_execution.name
}

output "ecs_execution_role_arn" {
  description = "ECS task execution IAM role ARN"
  value       = aws_iam_role.ecs_execution.arn
}

# ============================================================
# ECS TASK ROLE
# ============================================================

output "ecs_task_role_id" {
  description = "ECS task IAM role ID"
  value       = aws_iam_role.ecs_task.id
}

output "ecs_task_role_name" {
  description = "ECS task IAM role name"
  value       = aws_iam_role.ecs_task.name
}

output "ecs_task_role_arn" {
  description = "ECS task IAM role ARN"
  value       = aws_iam_role.ecs_task.arn
}

# ============================================================
# CLOUDWATCH LOG GROUPS
# ============================================================

output "ecs_exec_log_group_name" {
  description = "CloudWatch log group for ECS Exec"
  value       = aws_cloudwatch_log_group.ecs_exec.name
}

output "ecs_exec_log_group_arn" {
  description = "CloudWatch log group ARN for ECS Exec"
  value       = aws_cloudwatch_log_group.ecs_exec.arn
}

output "backend_log_group_name" {
  description = "Backend CloudWatch log group name"
  value       = aws_cloudwatch_log_group.backend.name
}

output "backend_log_group_arn" {
  description = "Backend CloudWatch log group ARN"
  value       = aws_cloudwatch_log_group.backend.arn
}

output "worker_log_group_name" {
  description = "Celery worker CloudWatch log group name"
  value       = aws_cloudwatch_log_group.worker.name
}

output "worker_log_group_arn" {
  description = "Celery worker CloudWatch log group ARN"
  value       = aws_cloudwatch_log_group.worker.arn
}

output "frontend_log_group_name" {
  description = "Frontend CloudWatch log group name"
  value       = aws_cloudwatch_log_group.frontend.name
}

output "frontend_log_group_arn" {
  description = "Frontend CloudWatch log group ARN"
  value       = aws_cloudwatch_log_group.frontend.arn
}

output "resume_processing_log_group_name" {
  description = "Resume processing CloudWatch log group name"
  value       = aws_cloudwatch_log_group.resume_processing.name
}

output "resume_processing_log_group_arn" {
  description = "Resume processing CloudWatch log group ARN"
  value       = aws_cloudwatch_log_group.resume_processing.arn
}

output "interview_processing_log_group_name" {
  description = "Interview processing CloudWatch log group name"
  value       = aws_cloudwatch_log_group.interview_processing.name
}

output "interview_processing_log_group_arn" {
  description = "Interview processing CloudWatch log group ARN"
  value       = aws_cloudwatch_log_group.interview_processing.arn
}

output "ai_processing_log_group_name" {
  description = "AI processing CloudWatch log group name"
  value       = aws_cloudwatch_log_group.ai_processing.name
}

output "ai_processing_log_group_arn" {
  description = "AI processing CloudWatch log group ARN"
  value       = aws_cloudwatch_log_group.ai_processing.arn
}

output "rag_processing_log_group_name" {
  description = "RAG processing CloudWatch log group name"
  value       = aws_cloudwatch_log_group.rag_processing.name
}

output "rag_processing_log_group_arn" {
  description = "RAG processing CloudWatch log group ARN"
  value       = aws_cloudwatch_log_group.rag_processing.arn
}

output "report_processing_log_group_name" {
  description = "Report processing CloudWatch log group name"
  value       = aws_cloudwatch_log_group.report_processing.name
}

output "report_processing_log_group_arn" {
  description = "Report processing CloudWatch log group ARN"
  value       = aws_cloudwatch_log_group.report_processing.arn
}