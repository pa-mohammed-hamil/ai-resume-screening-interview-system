# ============================================================
# CloudWatch Custom Metrics
# AI Resume Screening & Interview System
# ============================================================

locals {
  metric_namespace = "${var.project_name}/Application"

  ai_metric_namespace         = "${var.project_name}/AI"
  interview_metric_namespace  = "${var.project_name}/Interview"
  celery_metric_namespace     = "${var.project_name}/Celery"
  database_metric_namespace   = "${var.project_name}/Database"
  security_metric_namespace   = "${var.project_name}/Security"
}

# ============================================================
# Application Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "application_health" {
  name           = "${var.project_name}-application-health"
  log_group_name = aws_cloudwatch_log_group.application.name

  # Application should log:
  # application_health=1
  pattern = "application_health=1"

  metric_transformation {
    name          = "ApplicationHealth"
    namespace     = local.metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "api_latency" {
  name           = "${var.project_name}-api-latency"
  log_group_name = aws_cloudwatch_log_group.application.name

  pattern = "?api_latency ?latency_ms"

  metric_transformation {
    name          = "APILatency"
    namespace     = local.metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "api_requests" {
  name           = "${var.project_name}-api-request-count"
  log_group_name = aws_cloudwatch_log_group.backend.name

  pattern = "?GET ?POST ?PUT ?PATCH ?DELETE"

  metric_transformation {
    name          = "APIRequests"
    namespace     = local.metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "api_errors" {
  name           = "${var.project_name}-api-error-count"
  log_group_name = aws_cloudwatch_log_group.backend.name

  pattern = "?ERROR ?Exception ?InternalServerError"

  metric_transformation {
    name          = "APIErrors"
    namespace     = local.metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# Resume Processing Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "resumes_uploaded" {
  name           = "${var.project_name}-resumes-uploaded"
  log_group_name = aws_cloudwatch_log_group.application.name

  pattern = "?resume_uploaded ?file_uploaded"

  metric_transformation {
    name          = "ResumesUploaded"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "resume_parsing_completed" {
  name           = "${var.project_name}-resume-parsing-completed"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?resume_parsed ?resume_parsing_completed"

  metric_transformation {
    name          = "ResumeParsingCompleted"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "resume_processing_errors" {
  name           = "${var.project_name}-resume-processing-errors"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?resume_processing_failed ?resume_parsing_failed"

  metric_transformation {
    name          = "ResumeProcessingErrors"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# ATS Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "ats_scores_generated" {
  name           = "${var.project_name}-ats-scores-generated"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?ats_score_generated ?ats_scoring_completed"

  metric_transformation {
    name          = "ATSScoringCount"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "ats_scoring_errors" {
  name           = "${var.project_name}-ats-scoring-errors"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?ats_scoring_failed ?ats_score_error"

  metric_transformation {
    name          = "ATSScoringErrors"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# Resume / Job Matching Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "resume_matching" {
  name           = "${var.project_name}-resume-matching"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?resume_job_match ?matching_completed"

  metric_transformation {
    name          = "ResumeMatchingCount"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "matching_errors" {
  name           = "${var.project_name}-matching-errors"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?matching_failed ?matching_error"

  metric_transformation {
    name          = "MatchingErrors"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# Candidate Ranking Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "candidate_ranking" {
  name           = "${var.project_name}-candidate-ranking"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?candidate_ranked ?ranking_completed"

  metric_transformation {
    name          = "CandidateRankingCount"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "ranking_errors" {
  name           = "${var.project_name}-candidate-ranking-errors"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?ranking_failed ?ranking_error"

  metric_transformation {
    name          = "CandidateRankingErrors"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# Skill Intelligence Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "skill_extraction" {
  name           = "${var.project_name}-skill-extraction"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?skills_extracted ?skill_extraction_completed"

  metric_transformation {
    name          = "SkillExtractionCount"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "skill_gap_analysis" {
  name           = "${var.project_name}-skill-gap-analysis"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?skill_gap_completed ?skill_gap_analysis"

  metric_transformation {
    name          = "SkillGapAnalysisCount"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# JD Analysis Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "jd_analysis" {
  name           = "${var.project_name}-jd-analysis"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?jd_analysis_completed ?job_description_analyzed"

  metric_transformation {
    name          = "JDAnalysisCount"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "jd_analysis_errors" {
  name           = "${var.project_name}-jd-analysis-errors"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?jd_analysis_failed ?jd_analysis_error"

  metric_transformation {
    name          = "JDAnalysisErrors"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# Resume Optimizer Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "resume_optimization" {
  name           = "${var.project_name}-resume-optimization"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?resume_optimized ?optimization_completed"

  metric_transformation {
    name          = "ResumeOptimizationCount"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# AI / LLM Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "llm_requests" {
  name           = "${var.project_name}-llm-requests"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?llm_request ?llm_completion"

  metric_transformation {
    name          = "LLMRequests"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "llm_errors" {
  name           = "${var.project_name}-llm-errors"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?llm_error ?model_error ?openai_error"

  metric_transformation {
    name          = "LLMErrors"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "llm_timeout" {
  name           = "${var.project_name}-llm-timeouts"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?llm_timeout ?model_timeout"

  metric_transformation {
    name          = "LLMTimeouts"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# RAG Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "rag_queries" {
  name           = "${var.project_name}-rag-queries"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?rag_query ?rag_retrieval"

  metric_transformation {
    name          = "RAGQueries"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "rag_errors" {
  name           = "${var.project_name}-rag-errors"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?rag_error ?retrieval_error"

  metric_transformation {
    name          = "RAGErrors"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# Interview Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "interview_started" {
  name           = "${var.project_name}-interview-started"
  log_group_name = aws_cloudwatch_log_group.interview_engine.name

  pattern = "?interview_started ?interview_session_started"

  metric_transformation {
    name          = "InterviewSessions"
    namespace     = local.interview_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "interview_completed" {
  name           = "${var.project_name}-interview-completed"
  log_group_name = aws_cloudwatch_log_group.interview_engine.name

  pattern = "?interview_completed ?interview_finished"

  metric_transformation {
    name          = "InterviewCompleted"
    namespace     = local.interview_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "interview_errors" {
  name           = "${var.project_name}-interview-errors"
  log_group_name = aws_cloudwatch_log_group.interview_engine.name

  pattern = "?interview_error ?interview_failed ?Exception"

  metric_transformation {
    name          = "InterviewErrors"
    namespace     = local.interview_metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# Interview Questions
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "questions_generated" {
  name           = "${var.project_name}-questions-generated"
  log_group_name = aws_cloudwatch_log_group.interview_engine.name

  pattern = "?question_generated ?next_question_generated"

  metric_transformation {
    name          = "QuestionsGenerated"
    namespace     = local.interview_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "answers_evaluated" {
  name           = "${var.project_name}-answers-evaluated"
  log_group_name = aws_cloudwatch_log_group.interview_engine.name

  pattern = "?answer_evaluated ?answer_evaluation_completed"

  metric_transformation {
    name          = "AnswersEvaluated"
    namespace     = local.interview_metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# Voice Interview Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "speech_to_text" {
  name           = "${var.project_name}-speech-to-text"
  log_group_name = aws_cloudwatch_log_group.interview_engine.name

  pattern = "?speech_to_text ?transcription_completed"

  metric_transformation {
    name          = "SpeechToTextRequests"
    namespace     = local.interview_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "text_to_speech" {
  name           = "${var.project_name}-text-to-speech"
  log_group_name = aws_cloudwatch_log_group.interview_engine.name

  pattern = "?text_to_speech ?tts_completed"

  metric_transformation {
    name          = "TextToSpeechRequests"
    namespace     = local.interview_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "voice_processing_errors" {
  name           = "${var.project_name}-voice-processing-errors"
  log_group_name = aws_cloudwatch_log_group.interview_engine.name

  pattern = "?voice_processing_failed ?transcription_failed ?tts_failed"

  metric_transformation {
    name          = "VoiceProcessingErrors"
    namespace     = local.interview_metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# Interview Report Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "interview_reports" {
  name           = "${var.project_name}-interview-reports"
  log_group_name = aws_cloudwatch_log_group.interview_engine.name

  pattern = "?interview_report_generated ?report_generated"

  metric_transformation {
    name          = "InterviewReportsGenerated"
    namespace     = local.interview_metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# Celery Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "celery_tasks_started" {
  name           = "${var.project_name}-celery-task-started"
  log_group_name = aws_cloudwatch_log_group.celery.name

  pattern = "?task_started ?celery_task_started"

  metric_transformation {
    name          = "CeleryTasksStarted"
    namespace     = local.celery_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "celery_tasks_completed" {
  name           = "${var.project_name}-celery-task-completed"
  log_group_name = aws_cloudwatch_log_group.celery.name

  pattern = "?SUCCESS ?task_completed"

  metric_transformation {
    name          = "CeleryTaskCompleted"
    namespace     = local.celery_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "celery_task_failures" {
  name           = "${var.project_name}-celery-task-failures"
  log_group_name = aws_cloudwatch_log_group.celery.name

  pattern = "?FAILURE ?task_failed ?Exception"

  metric_transformation {
    name          = "CeleryTaskFailures"
    namespace     = local.celery_metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# Database Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "database_errors" {
  name           = "${var.project_name}-database-errors"
  log_group_name = aws_cloudwatch_log_group.database.name

  pattern = "?ERROR ?FATAL ?deadlock"

  metric_transformation {
    name          = "DatabaseErrors"
    namespace     = local.database_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "database_slow_queries" {
  name           = "${var.project_name}-database-slow-queries"
  log_group_name = aws_cloudwatch_log_group.database.name

  pattern = "?slow_query ?query_timeout"

  metric_transformation {
    name          = "SlowQueries"
    namespace     = local.database_metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# Security Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "authentication_failures" {
  name           = "${var.project_name}-authentication-failures"
  log_group_name = aws_cloudwatch_log_group.audit.name

  pattern = "?authentication_failed ?login_failed ?invalid_token"

  metric_transformation {
    name          = "AuthenticationFailures"
    namespace     = local.security_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "unauthorized_requests" {
  name           = "${var.project_name}-unauthorized-requests"
  log_group_name = aws_cloudwatch_log_group.audit.name

  pattern = "?unauthorized ?forbidden"

  metric_transformation {
    name          = "UnauthorizedRequests"
    namespace     = local.security_metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# Custom Application Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "candidate_created" {
  name           = "${var.project_name}-candidate-created"
  log_group_name = aws_cloudwatch_log_group.application.name

  pattern = "?candidate_created ?candidate_registered"

  metric_transformation {
    name          = "CandidatesCreated"
    namespace     = local.metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "jobs_created" {
  name           = "${var.project_name}-jobs-created"
  log_group_name = aws_cloudwatch_log_group.application.name

  pattern = "?job_created ?job_posted"

  metric_transformation {
    name          = "JobsCreated"
    namespace     = local.metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "resume_downloads" {
  name           = "${var.project_name}-resume-downloads"
  log_group_name = aws_cloudwatch_log_group.application.name

  pattern = "?resume_downloaded ?resume_exported"

  metric_transformation {
    name          = "ResumeDownloads"
    namespace     = local.metric_namespace
    value         = "1"
    default_value = 0
  }
}

# ============================================================
# Fairness / Bias Metrics
# ============================================================

resource "aws_cloudwatch_log_metric_filter" "fairness_evaluations" {
  name           = "${var.project_name}-fairness-evaluations"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?fairness_evaluation ?fairness_report"

  metric_transformation {
    name          = "FairnessEvaluations"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}

resource "aws_cloudwatch_log_metric_filter" "bias_detected" {
  name           = "${var.project_name}-bias-detected"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name

  pattern = "?bias_detected ?potential_bias"

  metric_transformation {
    name          = "BiasDetected"
    namespace     = local.ai_metric_namespace
    value         = "1"
    default_value = 0
  }
}