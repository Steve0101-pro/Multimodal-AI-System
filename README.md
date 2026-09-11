# 🧠 Document Intelligence

> **Production-grade multimodal document intelligence platform built
> with FastAPI, Streamlit, PostgreSQL, Redis, Supabase Storage, NVIDIA
> VLM, Groq Whisper, Gemini, LangSmith, and AWS.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](#)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white)](#)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)](#)
[![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?logo=redis&logoColor=white)](#)
[![AWS](https://img.shields.io/badge/AWS-Production-232F3E?logo=amazonaws&logoColor=white)](#)
[![LangSmith](https://img.shields.io/badge/LangSmith-Observability-1C1C1C)](#)

------------------------------------------------------------------------

## ✨ What is this?

**Document Intelligence** is a production-oriented AI application for
turning documents, images, audio, and multimodal questions into
structured, useful answers.

The platform supports two major workflows:

### 📄 Document Intelligence

Upload an invoice or supported document image and run:

-   OCR and text extraction
-   Layout-aware extraction
-   Structured invoice extraction
-   Vision-language model analysis
-   Persistent document storage

### 🎙️ Multimodal Intelligence

Send:

-   🎤 an audio question
-   🖼️ an optional image
-   🧠 conversational context

The system can combine speech recognition, vision, reasoning, and
text-to-speech into a single multimodal workflow.

------------------------------------------------------------------------

# 🚀 Core Capabilities

  -----------------------------------------------------------------------
  Capability                          What it provides
  ----------------------------------- -----------------------------------
  🔐 Authentication                   JWT registration, login, password
                                      recovery, protected APIs

  👥 Authorization                    User ownership and
                                      administrator-controlled review
                                      workflows

  📄 OCR                              Extract text from supported
                                      document images

  👁️ VLM extraction                   Vision-language analysis and
                                      structured invoice extraction

  🎤 Speech-to-text                   Audio question processing through
                                      Groq

  🧠 Multimodal reasoning             Gemini-based reasoning over text,
                                      audio-derived context, and images

  🔊 Text-to-speech                   Native Gemini speech generation

  🗄️ Storage                          Supabase Storage for
                                      uploaded/generated assets

  🐘 Database                         Async SQLAlchemy + PostgreSQL

  ⚡ Caching                          Redis-backed caching and runtime
                                      support

  📊 Observability                    LangSmith tracing and application
                                      monitoring

  🧪 Evaluation                       Versioned offline evaluation suite
                                      and regression gates

  ⚖️ Human review                     User feedback and administrator
                                      review queue

  🛡️ AI safety                        Prompt-injection and
                                      credential-exfiltration checks

  🐳 Containers                       Separate API and Streamlit images

  🔄 CI/CD                            Automated image build, registry
                                      push, and production deployment

  ☁️ AWS                              Production deployment behind an
                                      Application Load Balancer
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 🏗️ System Architecture

``` text
                                  ┌──────────────────────┐
                                  │      User / Browser  │
                                  └──────────┬───────────┘
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │    Streamlit UI      │
                                  │       :8501          │
                                  └──────────┬───────────┘
                                             │
                                             ▼
                           ┌────────────────────────────────┐
                           │        FastAPI Backend :8000   │
                           │                                │
                           │  Auth • Documents • Multimodal│
                           │  Feedback • Health • Monitoring│
                           └───────┬─────────┬─────────┬────┘
                                   │         │         │
                    ┌──────────────┘         │         └──────────────┐
                    ▼                        ▼                        ▼
             ┌─────────────┐        ┌─────────────┐        ┌────────────────┐
             │ PostgreSQL  │        │    Redis    │        │ AI / Providers │
             │             │        │             │        │                │
             │ Users       │        │ Cache       │        │ NVIDIA VLM     │
             │ Documents   │        │ Runtime     │        │ Groq Whisper   │
             │ Feedback    │        │ Support     │        │ Gemini          │
             │ Audit data  │        │             │        │ Portkey        │
             └─────────────┘        └─────────────┘        └───────┬────────┘
                                                                    │
                                                                    ▼
                                                           ┌────────────────┐
                                                           │ Supabase       │
                                                           │ Storage        │
                                                           └────────────────┘

                           Observability / Evaluation
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
              ┌────────────┐                    ┌────────────┐
              │ LangSmith  │                    │ Eval Suite │
              │ Tracing    │                    │ + Review   │
              └────────────┘                    └────────────┘
```

## 🔁 Multimodal request flow

``` text
Audio + optional Image
        │
        ▼
 FastAPI /multimodal
        │
        ├──► Safety checks
        │
        ├──► Groq Whisper
        │       └──► Transcript
        │
        ├──► Gemini multimodal reasoning
        │       ├── transcript
        │       ├── image
        │       ├── conversation context
        │       └── optional tools
        │
        └──► Gemini TTS
                │
                ▼
          Audio response
                │
                ▼
             Streamlit
```

------------------------------------------------------------------------

# 🧩 Technology Stack

### Backend

-   **FastAPI** --- asynchronous REST API
-   **Pydantic / Pydantic Settings** --- validation and configuration
-   **SQLAlchemy Async** --- database access
-   **Alembic** --- schema migrations
-   **JWT** --- authentication
-   **Redis** --- caching/runtime support

### AI

-   **NVIDIA VLM** --- vision and document extraction
-   **Portkey** --- AI gateway/provider routing
-   **Groq Whisper** --- speech-to-text
-   **Nnvidia Nemotrome** --- multimodal reasoning upgraded 
-   **Gemini TTS** --- native speech generation

### Data & Storage

-   **PostgreSQL**
-   **Supabase Storage**
-   **Redis**

### Observability & Evaluation

-   **LangSmith**
-   Offline regression evaluation
-   LLM-as-judge evaluation
-   Human review workflows
-   Append-only evaluation/audit metadata

### Deployment

-   Docker
-   GitHub Actions
-   Amazon ECR
-   Amazon ECS
-   Application Load Balancer
-   AWS security groups

------------------------------------------------------------------------

# 📁 Project Structure

``` text
document-intelligence/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schema.py
│   │
│   ├── api/
│   │   ├── auth.py
│   │   ├── documents.py
│   │   ├── multimodal_router.py
│   │   ├── feedback.py
│   │   └── monitoring.py
│   │
│   ├── dependencies/
│   │   └── auth.py
│   │
│   └── services/
│       ├── ocr_service.py
│       ├── vlm_service.py
│       ├── stt_services.py
│       ├── tts_services.py
│       ├── multimodal.py
│       ├── storage.py
│       ├── cache.py
│       └── portkeys_service.py
│
├── evals/
│   ├── golden cases
│   ├── responses.json
│   └── run_offline.py
│
├── tests/
│
├── alembic/
│
├── streamlit_app.py
├── Dockerfile.api
├── Dockerfile.ui
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── .github/
    └── workflows/
        └── CI/CD workflow
```

------------------------------------------------------------------------

# ⚙️ Configuration

Create a `.env` file in the project root.

> ⚠️ **Never commit production secrets to Git.**

``` env
# -----------------------------
# Database
# -----------------------------
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/document_intelligence

# -----------------------------
# Redis
# -----------------------------
REDIS_URL=redis://host:6379/0

# -----------------------------
# Authentication
# -----------------------------
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# -----------------------------
# Application
# -----------------------------
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:8501

# -----------------------------
# Gemini
# -----------------------------
GEMINI_API_KEY=replace-me
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TTS_MODEL=gemini-2.0-flash

# -----------------------------
# Groq
# -----------------------------
GROQ_API_KEY=replace-me
GROQ_MODEL=mixtral-8x7b-32768

# -----------------------------
# NVIDIA
# -----------------------------
NVIDIA_API_KEY=replace-me
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_PRIMARY_MODEL=meta/llama-3.2-90b-vision-instruct

# -----------------------------
# Supabase
# -----------------------------
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=replace-me
SUPABASE_BUCKET_NAME=documents

# -----------------------------
# Portkey
# -----------------------------
PORTKEYS_ENABLED=false
PORTKEYS_API_KEY=

# -----------------------------
# Evaluation
# -----------------------------
ONLINE_EVAL_ENABLED=false
ONLINE_EVAL_SAMPLE_RATE=1.0
```

------------------------------------------------------------------------

# 💻 Local Development

## 1. Create / activate the environment

Windows PowerShell:

``` powershell
.\doc-intell\Scripts\Activate.ps1
```

Install dependencies:

``` powershell
pip install -r requirements.txt
```

## 2. Run migrations

``` powershell
alembic upgrade head
```

## 3. Start FastAPI

``` powershell
uvicorn app.main:app --reload
```

API:

``` text
http://localhost:8000
```

Swagger:

``` text
http://localhost:8000/docs
```

## 4. Start Streamlit

In a second terminal:

``` powershell
streamlit run streamlit_app.py
```

UI:

``` text
http://localhost:8501
```

------------------------------------------------------------------------

# 🔌 API

  Method    Endpoint                      Purpose
  --------- ----------------------------- ---------------------------------
  `POST`    `/auth/register`              Register a user and return JWT
  `POST`    `/auth/login`                 Authenticate and return JWT
  `POST`    `/auth/forgot-password`       Start password recovery
  `POST`    `/auth/reset-password`        Consume a password-reset token
  `POST`    `/documents/`                 OCR + structured extraction
  `POST`    `/documents/vlm`              VLM document extraction
  `POST`    `/multimodal/voice-image`     Audio + optional image workflow
  `GET`     `/multimodal/conversations`   List user conversations
  `GET`     `/health/full`                API + Redis health
  `POST`    `/feedback`                   Submit feedback
  `GET`     `/feedback/review-queue`      Admin review queue
  `PATCH`   `/feedback/{id}/review`       Review / resolve feedback

Protected endpoints require:

``` http
Authorization: Bearer <JWT>
```

------------------------------------------------------------------------

# 🧪 Evaluation & Quality Gates

The project includes a **versioned offline evaluation suite** designed
to prevent prompt/model regressions from reaching production unnoticed.

## Run the evaluator

Create a response map:

``` powershell
@'
{
  "invoice-total-001": "The invoice total is 125 dollars.",
  "uncertain-001": "The missing information is the due date."
}
'@ | Set-Content evals/responses.json
```

Run:

``` powershell
.\doc-intell\Scripts\python.exe evals/run_offline.py evals/responses.json
```

The evaluator:

1.  Loads versioned golden cases.
2.  Scores candidate responses.
3.  Calculates the regression pass rate.
4.  Compares the result against the configured threshold.
5.  Returns a non-zero exit code when the quality gate fails.

### Recommended production lifecycle

``` text
Prompt / Model Change
        │
        ▼
Offline Evaluation
        │
   ┌────┴────┐
   │         │
 FAIL       PASS
   │         │
 STOP       ▼
          Deploy
            │
            ▼
      Online Monitoring
            │
            ▼
      User Feedback
            │
            ▼
       Human Review
            │
            ▼
      Improve + Re-evaluate
```

------------------------------------------------------------------------

# 🛡️ AI Safety

The multimodal pipeline applies defense-in-depth checks before model
execution.

## Prompt injection

Inputs are checked for common instruction-override patterns designed to
manipulate the model's system behavior.

## Credential exfiltration

Inputs are checked for common attempts to obtain:

-   API keys
-   passwords
-   secrets
-   credentials
-   internal configuration

## Important security principle

These checks are **not a complete security boundary**.

Production security should also include:

-   provider-side safety controls
-   strict outbound network policies
-   secret isolation
-   redaction
-   authentication and authorization
-   resource ownership checks
-   least-privilege credentials
-   human review for sensitive cases
-   audit logging

------------------------------------------------------------------------

# 👤 Human Review & Feedback

Users can submit feedback on model responses.

Administrators can access the review queue and resolve submitted
feedback.

This creates a continuous improvement loop:

``` text
User
 │
 ▼
AI Response
 │
 ├── 👍 Positive
 │
 └── 👎 Negative
       │
       ▼
   Review Queue
       │
       ▼
 Human Review
       │
       ▼
 Prompt / Model / Safety Improvement
```

------------------------------------------------------------------------

# 📊 Online Evaluation

Online LLM-as-judge evaluation is **disabled by default** and is
designed to fail open.

Enable it with:

``` env
ONLINE_EVAL_ENABLED=true
ONLINE_EVAL_SAMPLE_RATE=1.0
OPENAI_API_KEY=replace-me
```

Evaluation metadata is written to the append-only audit log.

Raw prompts and model responses are not stored with evaluation records.

Administrators can inspect recent evaluation records through:

``` text
GET /monitoring/evaluations
```

------------------------------------------------------------------------

# 🔬 Testing

Run the complete automated test suite:

``` powershell
.\doc-intell\Scripts\python.exe -m pytest -q
```

Tests mock external provider calls, so they do not validate live
credentials.

> ⚠️ Live provider smoke tests should be executed intentionally because
> they consume provider quota.

------------------------------------------------------------------------

# 🐳 Docker

The project uses separate containers for the API and Streamlit UI.

``` text
Dockerfile.api  → FastAPI
Dockerfile.ui   → Streamlit
```

For a pull-only runtime stack:

``` bash
docker compose pull
docker compose up -d --no-build
docker compose ps
```

The runtime should consume pre-built images rather than building
production images on the server.

------------------------------------------------------------------------

# 🔄 CI/CD

Production images are built by **GitHub Actions**, not on the production
runtime.

``` text
Developer
    │
    │ git push
    ▼
GitHub
    │
    ▼
GitHub Actions
    │
    ├── Run tests
    │
    ├── Build API image
    ├── Build UI image
    │
    ▼
Amazon ECR
    │
    ▼
Amazon ECS
    │
    ▼
Application Load Balancer
    │
    ├── :8501 → Streamlit
    │
    └── :8000 → FastAPI
```

### Deployment principle

Production servers **pull immutable build artifacts** rather than
building application images themselves.

The deployment workflow can publish images using:

-   `latest`
-   commit SHA

The commit SHA provides an exact deployment artifact and makes
rollback/debugging easier.

------------------------------------------------------------------------

# ☁️ AWS Production Architecture

The production deployment uses:

-   **Amazon ECR** --- container image registry
-   **Amazon ECS** --- container orchestration
-   **Application Load Balancer** --- HTTP routing
-   **Security Groups** --- network access control
-   **CloudWatch** --- application/container logs

The API and UI run as separate services.

``` text
                         Internet
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Application Load     │
                 │ Balancer             │
                 └──────────┬──────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
        Streamlit :8501              FastAPI :8000
              │                           │
              │                     ┌─────┴─────┐
              │                     │           │
              ▼                     ▼           ▼
             UI                  Database     Redis
                                    │
                                    ▼
                              AI / Storage
```

### Long-running multimodal requests

Multimodal inference can involve several upstream AI calls, particularly
when speech generation is included.

The production ALB idle timeout should therefore be configured with
enough headroom for the application-level Gemini timeout.

Current application behavior uses a **120-second TTS request timeout**.

A small additional ALB timeout margin is recommended so the gateway does
not terminate a request at exactly the same moment as the application
timeout.

------------------------------------------------------------------------

# 🔐 Production Security Checklist

Before exposing the application publicly:

-   [ ] Use strong JWT secrets.
-   [ ] Keep all provider keys outside Git.
-   [ ] Use production-grade PostgreSQL.
-   [ ] Use managed Redis where appropriate.
-   [ ] Restrict `CORS_ORIGINS`.
-   [ ] Never use `CORS_ORIGINS=*` in production.
-   [ ] Enforce authentication on protected endpoints.
-   [ ] Enforce resource ownership.
-   [ ] Keep administrator routes restricted.
-   [ ] Use least-privilege cloud credentials.
-   [ ] Enable TLS/HTTPS at the public edge.
-   [ ] Configure database backups.
-   [ ] Monitor application and infrastructure health.
-   [ ] Run offline evaluation before model/prompt rollout.
-   [ ] Keep an audit trail for security-sensitive operations.
-   [ ] Review prompt-injection and data-exfiltration defenses
    regularly.

------------------------------------------------------------------------

# 🩺 Health & Operations

Health endpoint:

``` text
GET /health/full
```

Use it to verify API and Redis availability.

For production incidents, inspect:

1.  Application logs
2.  ECS task health
3.  ALB target health
4.  CloudWatch logs
5.  Database connectivity
6.  Redis connectivity
7.  Provider availability
8.  Request latency and gateway timeouts

------------------------------------------------------------------------

# 📈 Observability

The application is designed around observable AI workflows.

``` text
User Request
     │
     ▼
FastAPI
     │
     ├── Auth trace
     ├── Retrieval / processing trace
     ├── VLM trace
     ├── STT trace
     ├── Gemini reasoning trace
     ├── TTS trace
     │
     ▼
LangSmith
     │
     ▼
Evaluation / Feedback
```

Tracing helps identify whether latency or failures originate from:

-   application code
-   database
-   Redis
-   AI provider
-   TTS
-   network/gateway infrastructure

------------------------------------------------------------------------

# 🧱 Reliability Principles

This project follows several production-oriented principles:

### 1. Fail explicitly

Provider failures should surface as controlled application errors rather
than silently producing incorrect output.

### 2. Validate at boundaries

Validate:

-   authentication
-   file types
-   request payloads
-   model responses
-   structured JSON
-   ownership
-   configuration

### 3. Keep secrets out of source control

Production credentials belong in environment configuration or a secrets
manager.

### 4. Evaluate before deployment

Prompt and model changes should pass the offline regression suite before
production rollout.

### 5. Observe after deployment

Passing tests is not enough. Production behavior must be monitored
through traces, health checks, feedback, and evaluation.

### 6. Separate build from runtime

CI builds the artifacts. Production pulls and runs those artifacts.

------------------------------------------------------------------------

# 🗺️ Recommended Development Workflow

``` text
1. Build feature
      │
      ▼
2. Write / update tests
      │
      ▼
3. Run pytest
      │
      ▼
4. Run offline evaluation
      │
      ▼
5. Review safety implications
      │
      ▼
6. Commit + push
      │
      ▼
7. GitHub Actions
      │
      ▼
8. Build + publish image
      │
      ▼
9. Deploy to ECS
      │
      ▼
10. Verify health
      │
      ▼
11. Test production workflow
      │
      ▼
12. Monitor LangSmith / CloudWatch
```

------------------------------------------------------------------------

# 🎯 Project Goals

This project demonstrates how to move beyond a simple AI prototype
toward a **production multimodal AI system** with:

-   asynchronous APIs
-   authentication and authorization
-   persistent storage
-   caching
-   multimodal inference
-   speech processing
-   structured extraction
-   model observability
-   offline evaluation
-   LLM-as-judge evaluation
-   human review
-   AI safety controls
-   automated testing
-   containerization
-   CI/CD
-   AWS deployment
-   operational health monitoring

------------------------------------------------------------------------

# 🏁 Quick Start

``` powershell
# Install
pip install -r requirements.txt

# Database migrations
alembic upgrade head

# API
uvicorn app.main:app --reload

# UI
streamlit run streamlit_app.py
```

Then open:

``` text
UI       → http://localhost:8501
API      → http://localhost:8000
Swagger  → http://localhost:8000/docs
```

------------------------------------------------------------------------

# 📌 Production Notes

For a serious production deployment:

-   Prefer managed PostgreSQL such as RDS or Supabase.
-   Prefer managed Redis such as ElastiCache or an equivalent managed
    service.
-   Put HTTPS/TLS in front of public services.
-   Restrict CORS to the real frontend origin.
-   Maintain automated database backups.
-   Use Alembic for schema evolution.
-   Keep provider credentials in a secrets manager where possible.
-   Use exact image versions/commit SHAs for controlled releases.
-   Monitor ALB, ECS, application, database, Redis, and provider
    latency.
-   Run regression evaluation before changing production prompts or
    models.

------------------------------------------------------------------------

## 📚 Summary

**Document Intelligence** combines document AI, computer vision, speech,
multimodal reasoning, structured extraction, safety, evaluation,
observability, and cloud deployment into one production-oriented system.

It is intentionally designed not just to **call an AI model**, but to
demonstrate the engineering layers required to operate AI reliably in
production.

> **AI is the intelligence layer. Production engineering is what makes
> that intelligence usable, observable, secure, and reliable.**

------------------------------------------------------------------------

## 👨‍💻 Project Status

**Production-ready deployment completed.**

Core platform:

-   ✅ FastAPI API
-   ✅ Streamlit UI
-   ✅ JWT authentication
-   ✅ PostgreSQL
-   ✅ Redis
-   ✅ Supabase Storage
-   ✅ NVIDIA VLM
-   ✅ Groq STT
-   ✅ NvidiaNemotrone multimodal reasoning
-   ✅ Gemini TTS
-   ✅ LangSmith observability
-   ✅ Offline evaluation
-   ✅ Human review
-   ✅ AI safety checks
-   ✅ Automated testing
-   ✅ Docker
-   ✅ GitHub Actions CI/CD
-   ✅ Amazon ECR
-   ✅ Amazon ECS
-   ✅ Application Load Balancer

------------------------------------------------------------------------

```{=html}
<p align="center">
```
**Built as a production-oriented multimodal AI system.**

```{=html}
</p>
```
