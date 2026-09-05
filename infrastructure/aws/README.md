# AWS Infrastructure

AWS deployment infrastructure for the AI Resume Screening & Interview System.

## Components

- ECS/Fargate: application and worker containers
- RDS: PostgreSQL database
- S3: resumes, audio, reports, and generated files
- CloudWatch: logs, metrics, alarms, and dashboards

## Terraform

Each component directory contains Terraform configuration files. Configure AWS credentials and variables before applying.

Typical workflow:

```bash
terraform init
terraform validate
terraform plan
terraform apply
```

For production, use remote Terraform state and environment-specific variable files.
