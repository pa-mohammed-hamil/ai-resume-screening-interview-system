# ============================================================
# AI Resume Screening & Interview System
# AWS S3 Outputs
# File: infrastructure/aws/s3/outputs.tf
# ============================================================


# ============================================================
# RESUME BUCKET
# ============================================================

output "resumes_bucket_id" {
  description = "Resume S3 bucket name"
  value       = aws_s3_bucket.resumes.id
}

output "resumes_bucket_name" {
  description = "Resume S3 bucket name"
  value       = aws_s3_bucket.resumes.bucket
}

output "resumes_bucket_arn" {
  description = "Resume S3 bucket ARN"
  value       = aws_s3_bucket.resumes.arn
}

output "resumes_bucket_domain_name" {
  description = "Resume S3 bucket regional domain name"
  value       = aws_s3_bucket.resumes.bucket_regional_domain_name
}


# ============================================================
# GENERATED RESUME BUCKET
# ============================================================

output "generated_resumes_bucket_id" {
  description = "Generated resume S3 bucket name"
  value       = aws_s3_bucket.generated_resumes.id
}

output "generated_resumes_bucket_name" {
  description = "Generated resume S3 bucket name"
  value       = aws_s3_bucket.generated_resumes.bucket
}

output "generated_resumes_bucket_arn" {
  description = "Generated resume S3 bucket ARN"
  value       = aws_s3_bucket.generated_resumes.arn
}

output "generated_resumes_bucket_domain_name" {
  description = "Generated resume S3 bucket regional domain name"
  value       = aws_s3_bucket.generated_resumes.bucket_regional_domain_name
}


# ============================================================
# INTERVIEW AUDIO BUCKET
# ============================================================

output "interview_audio_bucket_id" {
  description = "Interview audio S3 bucket name"
  value       = aws_s3_bucket.interview_audio.id
}

output "interview_audio_bucket_name" {
  description = "Interview audio S3 bucket name"
  value       = aws_s3_bucket.interview_audio.bucket
}

output "interview_audio_bucket_arn" {
  description = "Interview audio S3 bucket ARN"
  value       = aws_s3_bucket.interview_audio.arn
}

output "interview_audio_bucket_domain_name" {
  description = "Interview audio S3 bucket regional domain name"
  value       = aws_s3_bucket.interview_audio.bucket_regional_domain_name
}


# ============================================================
# INTERVIEW REPORTS BUCKET
# ============================================================

output "interview_reports_bucket_id" {
  description = "Interview reports S3 bucket name"
  value       = aws_s3_bucket.interview_reports.id
}

output "interview_reports_bucket_name" {
  description = "Interview reports S3 bucket name"
  value       = aws_s3_bucket.interview_reports.bucket
}

output "interview_reports_bucket_arn" {
  description = "Interview reports S3 bucket ARN"
  value       = aws_s3_bucket.interview_reports.arn
}

output "interview_reports_bucket_domain_name" {
  description = "Interview reports S3 bucket regional domain name"
  value       = aws_s3_bucket.interview_reports.bucket_regional_domain_name
}


# ============================================================
# TEMPORARY BUCKET
# ============================================================

output "temporary_bucket_id" {
  description = "Temporary S3 bucket name"
  value       = aws_s3_bucket.temporary.id
}

output "temporary_bucket_name" {
  description = "Temporary S3 bucket name"
  value       = aws_s3_bucket.temporary.bucket
}

output "temporary_bucket_arn" {
  description = "Temporary S3 bucket ARN"
  value       = aws_s3_bucket.temporary.arn
}

output "temporary_bucket_domain_name" {
  description = "Temporary S3 bucket regional domain name"
  value       = aws_s3_bucket.temporary.bucket_regional_domain_name
}


# ============================================================
# ALL BUCKET NAMES
# ============================================================

output "bucket_names" {
  description = "Map of all S3 bucket names"

  value = {
    resumes = aws_s3_bucket.resumes.bucket

    generated_resumes = aws_s3_bucket.generated_resumes.bucket

    interview_audio = aws_s3_bucket.interview_audio.bucket

    interview_reports = aws_s3_bucket.interview_reports.bucket

    temporary = aws_s3_bucket.temporary.bucket
  }
}


# ============================================================
# ALL BUCKET ARNS
# ============================================================

output "bucket_arns" {
  description = "Map of all S3 bucket ARNs"

  value = {
    resumes = aws_s3_bucket.resumes.arn

    generated_resumes = aws_s3_bucket.generated_resumes.arn

    interview_audio = aws_s3_bucket.interview_audio.arn

    interview_reports = aws_s3_bucket.interview_reports.arn

    temporary = aws_s3_bucket.temporary.arn
  }
}


# ============================================================
# RESUME BUCKET ARN FOR IAM
# ============================================================

output "resumes_bucket_object_arn" {
  description = "ARN pattern for objects inside resume bucket"
  value       = "${aws_s3_bucket.resumes.arn}/*"
}


# ============================================================
# GENERATED RESUME OBJECT ARN
# ============================================================

output "generated_resumes_bucket_object_arn" {
  description = "ARN pattern for objects inside generated resume bucket"
  value       = "${aws_s3_bucket.generated_resumes.arn}/*"
}


# ============================================================
# INTERVIEW AUDIO OBJECT ARN
# ============================================================

output "interview_audio_bucket_object_arn" {
  description = "ARN pattern for objects inside interview audio bucket"
  value       = "${aws_s3_bucket.interview_audio.arn}/*"
}


# ============================================================
# INTERVIEW REPORT OBJECT ARN
# ============================================================

output "interview_reports_bucket_object_arn" {
  description = "ARN pattern for objects inside interview reports bucket"
  value       = "${aws_s3_bucket.interview_reports.arn}/*"
}


# ============================================================
# TEMPORARY OBJECT ARN
# ============================================================

output "temporary_bucket_object_arn" {
  description = "ARN pattern for objects inside temporary bucket"
  value       = "${aws_s3_bucket.temporary.arn}/*"
}