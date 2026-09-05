# Database

Database configuration, SQLAlchemy models, sessions, and Alembic migrations for the **AI Resume Screening & Interview System**.

---

## Directory Structure

```text
backend/app/database/
│
├── __init__.py
├── connection.py
├── session.py
├── base.py
│
└── migrations/
    ├── README.md
    ├── env.py
    ├── script.py.mako
    │
    └── versions/
        ├── 001_create_users_table.py
        ├── 002_create_jobs_table.py
        ├── 003_create_resumes_table.py
        ├── 004_create_candidates_table.py
        ├── 005_create_interviews_table.py
        ├── 006_create_scores_table.py
        ├── 007_create_audit_logs_table.py
        └── 008_add_indexes.py
```

---

## Database Technology

The backend uses:

* **PostgreSQL** — primary relational database
* **SQLAlchemy** — ORM and database abstraction
* **Alembic** — database schema migrations
* **AsyncPG** — asynchronous PostgreSQL driver for application runtime
* **Psycopg** — synchronous PostgreSQL driver used by Alembic migrations

---

## Database Architecture

```text
                    PostgreSQL
                        │
                        ▼
              ┌──────────────────┐
              │   SQLAlchemy ORM │
              └──────────────────┘
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
       connection.py          session.py
             │                     │
             └──────────┬──────────┘
                        ▼
                     base.py
                        │
                        ▼
                    Models
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
      User            Resume            Job
        │               │                │
        └───────────────┼────────────────┘
                        ▼
                    Candidate
                        │
                        ▼
                    Interview
                        │
                        ▼
                      Score
                        │
                        ▼
                   Audit Log
```

---

# Database Tables

## 1. Users

The `users` table stores recruiter, administrator, and application-user information.

```text
users
├── id
├── email
├── hashed_password
├── full_name
├── role
├── is_active
├── created_at
└── updated_at
```

Primary key:

```text
users.id
```

Unique field:

```text
users.email
```

---

## 2. Jobs

The `jobs` table stores job descriptions created by recruiters.

```text
jobs
├── id
├── user_id
├── title
├── description
├── requirements
├── responsibilities
├── location
├── employment_type
├── status
├── created_at
└── updated_at
```

Relationship:

```text
users.id
    │
    └──────< jobs.user_id
```

---

## 3. Resumes

The `resumes` table stores uploaded resumes and AI-extracted information.

```text
resumes
├── id
├── user_id
├── candidate_id
├── file_name
├── file_path
├── file_type
├── raw_text
├── parsed_data
├── ats_score
├── status
├── created_at
└── updated_at
```

The `parsed_data` field stores structured AI extraction such as:

```json
{
  "name": "Candidate Name",
  "skills": [
    "Python",
    "FastAPI",
    "PostgreSQL"
  ],
  "education": [],
  "experience": []
}
```

---

## 4. Candidates

The `candidates` table stores candidates associated with recruitment jobs.

```text
candidates
├── id
├── user_id
├── job_id
├── name
├── email
├── phone
├── status
├── match_score
├── skill_score
├── experience_score
├── ranking
├── created_at
└── updated_at
```

Candidate pipeline:

```text
new
 ↓
screening
 ↓
shortlisted
 ↓
interview
 ↓
selected / rejected
```

---

## 5. Interviews

The `interviews` table stores AI and recruiter interview sessions.

```text
interviews
├── id
├── user_id
├── candidate_id
├── job_id
├── interview_type
├── status
├── scheduled_at
├── started_at
├── completed_at
├── duration_seconds
├── overall_score
├── report_path
├── created_at
└── updated_at
```

Interview types can include:

```text
technical
behavioral
mixed
screening
```

Interview status:

```text
scheduled
in_progress
completed
cancelled
```

---

## 6. Scores

The `scores` table stores AI-generated candidate and interview scoring information.

```text
scores
├── id
├── candidate_id
├── job_id
├── resume_id
├── interview_id
├── ats_score
├── skill_score
├── experience_score
├── education_score
├── semantic_score
├── overall_score
├── explanation
└── created_at
```

Example scoring model:

```text
ATS Score
    │
    ├── Skill Score
    ├── Experience Score
    ├── Education Score
    └── Semantic Score
            │
            ▼
       Overall Score
```

---

## 7. Audit Logs

The `audit_logs` table records important application activities.

```text
audit_logs
├── id
├── user_id
├── action
├── entity_type
├── entity_id
├── description
├── ip_address
├── user_agent
├── metadata
└── created_at
```

Example actions:

```text
LOGIN
LOGOUT
CREATE_JOB
UPDATE_JOB
UPLOAD_RESUME
ANALYZE_RESUME
CREATE_CANDIDATE
CREATE_INTERVIEW
COMPLETE_INTERVIEW
DELETE_CANDIDATE
```

---

# Entity Relationships

```text
                         ┌─────────────┐
                         │    Users    │
                         └──────┬──────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
           Jobs             Resumes          Candidates
              │                 │                 │
              │                 │                 │
              └────────┬────────┴─────────────────┘
                       │
                       ▼
                  Candidates
                       │
                       ▼
                  Interviews
                       │
                       ▼
                    Scores

Users
  │
  └──────────────────────────► Audit Logs
```

---

# Migration System

Alembic manages database schema changes.

Migration files are located at:

```text
backend/app/database/migrations/versions/
```

Current migration chain:

```text
001_create_users_table.py
             ↓
002_create_jobs_table.py
             ↓
003_create_resumes_table.py
             ↓
004_create_candidates_table.py
             ↓
005_create_interviews_table.py
             ↓
006_create_scores_table.py
             ↓
007_create_audit_logs_table.py
             ↓
008_add_indexes.py
```

---

# Environment Configuration

Database configuration should be stored in `.env`.

Example:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/resume_ai
```

For Alembic, the migration environment converts the asynchronous URL to a synchronous PostgreSQL driver.

Do not commit real database credentials to Git.

---

# Running PostgreSQL

If PostgreSQL is installed locally:

```bash
createdb resume_ai
```

Or using Docker:

```bash
docker compose up -d postgres
```

Check running containers:

```bash
docker compose ps
```

---

# Installing Database Dependencies

Install the required Python packages:

```bash
pip install sqlalchemy
pip install alembic
pip install asyncpg
pip install psycopg[binary]
```

Or install the project's complete requirements:

```bash
pip install -r backend/requirements.txt
```

---

# Alembic Commands

## Check current migration

```bash
alembic current
```

## View migration history

```bash
alembic history
```

## Apply all migrations

```bash
alembic upgrade head
```

## Apply one migration

```bash
alembic upgrade +1
```

## Roll back one migration

```bash
alembic downgrade -1
```

## Roll back everything

```bash
alembic downgrade base
```

## Create a migration

```bash
alembic revision -m "description"
```

## Auto-generate migration

```bash
alembic revision --autogenerate -m "update database schema"
```

---

# Recommended Migration Workflow

When changing a SQLAlchemy model:

```text
1. Modify model
       ↓
2. Start PostgreSQL
       ↓
3. Generate migration
       ↓
4. Review migration
       ↓
5. Apply migration
       ↓
6. Test application
```

Example:

```bash
alembic revision --autogenerate -m "add candidate location"
```

Then:

```bash
alembic upgrade head
```

---

# Database Reset

For development only, the database can be reset with:

```bash
alembic downgrade base
alembic upgrade head
```

This removes all schema objects created by the migration chain and recreates them.

**Do not use this workflow on production databases unless you intentionally understand the consequences.**

---

# Production Migration

Before deploying:

```bash
alembic current
```

Then:

```bash
alembic upgrade head
```

Recommended deployment sequence:

```text
Application Build
       ↓
Database Backup
       ↓
Run Alembic Migration
       ↓
Verify Database
       ↓
Deploy Application
       ↓
Health Check
```

---

# Indexing

Migration `008_add_indexes.py` adds additional indexes for frequently queried fields.

Examples:

```text
jobs.created_at
jobs.employment_type

resumes.file_name
resumes.created_at

candidates.created_at
candidates.experience_score
candidates.(job_id, status)
candidates.(job_id, ranking)

interviews.created_at
interviews.interview_type
interviews.(status, scheduled_at)

scores.created_at
scores.skill_score
scores.semantic_score
scores.(candidate_id, job_id)

audit_logs.(entity_type, entity_id)
audit_logs.(user_id, created_at)
```

Indexes should be added based on actual query patterns and production performance measurements.

---

# Database Safety

Never commit:

```text
.env
database passwords
API keys
production credentials
private certificates
```

Use:

```text
.env.example
```

for documenting required environment variables.

---

# Backup

For PostgreSQL:

```bash
pg_dump -U postgres -d resume_ai > backup.sql
```

Restore:

```bash
psql -U postgres -d resume_ai < backup.sql
```

For production systems, use automated backups and test restoration procedures regularly.

---

# Testing

Database-related tests should verify:

```text
User creation
Job creation
Resume upload
Candidate creation
Interview creation
Score creation
Audit logging
Foreign-key relationships
Migration upgrades
Migration downgrades
Indexes
```

Run the project tests with:

```bash
pytest
```

---

# Health Check

The backend health endpoint should verify application/database availability.

Example:

```text
GET /api/health
```

Expected response:

```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

# Development Notes

Keep SQLAlchemy models and Alembic migrations synchronized.

When adding or changing database fields:

```text
models/
   ↓
Alembic revision
   ↓
migration review
   ↓
database upgrade
   ↓
tests
```

Never manually modify an already-applied production migration. Create a new migration instead.

---

## Summary

The database layer provides:

* PostgreSQL persistence
* SQLAlchemy ORM
* asynchronous application database access
* Alembic schema versioning
* user and authentication data
* jobs and recruitment data
* resume and AI analysis data
* candidate ranking data
* interview data
* AI scoring data
* audit logging
* query-performance indexes
* migration and rollback support
