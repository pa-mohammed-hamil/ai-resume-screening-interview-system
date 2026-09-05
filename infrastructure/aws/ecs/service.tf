# ============================================================
# AI Resume Screening & Interview System
# AWS ECS Services
# File: infrastructure/aws/ecs/service.tf
# ============================================================

# ============================================================
# FRONTEND ECS SERVICE
# ============================================================

resource "aws_ecs_service" "frontend" {
  name            = "${var.project_name}-frontend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.frontend.arn

  desired_count = var.frontend_desired_count

  launch_type = "FARGATE"

  platform_version = "LATEST"

  enable_execute_command = true

  health_check_grace_period_seconds = 60

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  network_configuration {
    subnets = var.public_subnet_ids

    security_groups = [
      var.frontend_security_group_id
    ]

    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.frontend_target_group_arn
    container_name   = "frontend"
    container_port   = 80
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  lifecycle {
    ignore_changes = [
      desired_count
    ]
  }

  tags = {
    Name        = "${var.project_name}-frontend-service"
    Project     = var.project_name
    Environment = var.environment
    Service     = "frontend"
    ManagedBy   = "Terraform"
  }

  depends_on = [
    aws_ecs_task_definition.frontend
  ]
}


# ============================================================
# BACKEND ECS SERVICE
# ============================================================

resource "aws_ecs_service" "backend" {
  name            = "${var.project_name}-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn

  desired_count = var.backend_desired_count

  launch_type = "FARGATE"

  platform_version = "LATEST"

  enable_execute_command = true

  health_check_grace_period_seconds = 120

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  network_configuration {
    subnets = var.private_subnet_ids

    security_groups = [
      var.backend_security_group_id
    ]

    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.backend_target_group_arn
    container_name   = "backend"
    container_port   = 8000
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  lifecycle {
    ignore_changes = [
      desired_count
    ]
  }

  tags = {
    Name        = "${var.project_name}-backend-service"
    Project     = var.project_name
    Environment = var.environment
    Service     = "backend"
    ManagedBy   = "Terraform"
  }

  depends_on = [
    aws_ecs_task_definition.backend
  ]
}


# ============================================================
# CELERY WORKER ECS SERVICE
# ============================================================

resource "aws_ecs_service" "worker" {
  name            = "${var.project_name}-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn

  desired_count = var.worker_desired_count

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 70
    base              = 1
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 30
  }

  platform_version = "LATEST"

  enable_execute_command = true

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  network_configuration {
    subnets = var.private_subnet_ids

    security_groups = [
      var.worker_security_group_id
    ]

    assign_public_ip = false
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  lifecycle {
    ignore_changes = [
      desired_count
    ]
  }

  tags = {
    Name        = "${var.project_name}-worker-service"
    Project     = var.project_name
    Environment = var.environment
    Service     = "celery-worker"
    ManagedBy   = "Terraform"
  }

  depends_on = [
    aws_ecs_task_definition.worker
  ]
}


# ============================================================
# BACKEND SERVICE AUTOSCALING
# ============================================================

resource "aws_appautoscaling_target" "backend" {
  max_capacity       = var.backend_max_capacity
  min_capacity       = var.backend_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.backend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  depends_on = [
    aws_ecs_service.backend
  ]
}


# ============================================================
# BACKEND CPU AUTOSCALING
# ============================================================

resource "aws_appautoscaling_policy" "backend_cpu" {
  name               = "${var.project_name}-backend-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend.resource_id
  scalable_dimension = aws_appautoscaling_target.backend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = 70

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}


# ============================================================
# BACKEND MEMORY AUTOSCALING
# ============================================================

resource "aws_appautoscaling_policy" "backend_memory" {
  name               = "${var.project_name}-backend-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend.resource_id
  scalable_dimension = aws_appautoscaling_target.backend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = 75

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }

    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}


# ============================================================
# WORKER SERVICE AUTOSCALING
# ============================================================

resource "aws_appautoscaling_target" "worker" {
  max_capacity       = var.worker_max_capacity
  min_capacity       = var.worker_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.worker.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  depends_on = [
    aws_ecs_service.worker
  ]
}


# ============================================================
# WORKER CPU AUTOSCALING
# ============================================================

resource "aws_appautoscaling_policy" "worker_cpu" {
  name               = "${var.project_name}-worker-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.worker.resource_id
  scalable_dimension = aws_appautoscaling_target.worker.scalable_dimension
  service_namespace  = aws_appautoscaling_target.worker.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = 70

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}


# ============================================================
# WORKER MEMORY AUTOSCALING
# ============================================================

resource "aws_appautoscaling_policy" "worker_memory" {
  name               = "${var.project_name}-worker-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.worker.resource_id
  scalable_dimension = aws_appautoscaling_target.worker.scalable_dimension
  service_namespace  = aws_appautoscaling_target.worker.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = 75

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }

    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}


# ============================================================
# FRONTEND AUTOSCALING
# ============================================================

resource "aws_appautoscaling_target" "frontend" {
  max_capacity       = var.frontend_max_capacity
  min_capacity        = var.frontend_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.frontend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  depends_on = [
    aws_ecs_service.frontend
  ]
}


# ============================================================
# FRONTEND CPU AUTOSCALING
# ============================================================

resource "aws_appautoscaling_policy" "frontend_cpu" {
  name               = "${var.project_name}-frontend-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.frontend.resource_id
  scalable_dimension = aws_appautoscaling_target.frontend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.frontend.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = 70

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}


# ============================================================
# FRONTEND MEMORY AUTOSCALING
# ============================================================

resource "aws_appautoscaling_policy" "frontend_memory" {
  name               = "${var.project_name}-frontend-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.frontend.resource_id
  scalable_dimension = aws_appautoscaling_target.frontend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.frontend.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = 75

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }

    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}