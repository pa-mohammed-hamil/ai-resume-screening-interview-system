# Infrastructure

Deployment and infrastructure configuration for the AI Resume Screening & Interview System.

## Structure

- `docker/` - Dockerfiles for backend, frontend, and Celery workers
- `nginx/` - Nginx reverse proxy configuration
- `aws/` - AWS deployment configuration
- `monitoring/` - Prometheus, Grafana, and health checks

## Services

The production architecture can use:

- AWS ECS/Fargate for containers
- Amazon RDS PostgreSQL for the database
- Amazon S3 for resumes, interview audio, and reports
- Redis for Celery
- CloudWatch for AWS logs and metrics
- Prometheus/Grafana for application metrics

See `aws/README.md` for AWS deployment guidance.
