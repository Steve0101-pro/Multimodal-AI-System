# Document Intelligence

A FastAPI and Streamlit application for document extraction and multimodal questions. Upload an invoice for OCR or VLM analysis, or send an audio question with an optional image. The backend uses JWT authentication, PostgreSQL, Redis caching, Supabase Storage, and configurable AI providers.

## Features

- Versioned offline evaluation suite with regression pass-rate gates
- Prompt-injection and common credential-exfiltration input checks
- User feedback and admin-controlled human review queue
- EC2 deployment pulls pre-built images; EC2 never builds them

## Architecture

```text
Browser
  |
  v
Streamlit UI :8501  --->  FastAPI API :8000
                                  |
                 +----------------+----------------+
                 v                v                v
             PostgreSQL        Redis        AI / Storage providers
```

The Streamlit container reaches the API using the Docker Compose service name `http://api:8000`. Configure `CORS_ORIGINS` as a comma-separated list of allowed origins for browser-based API access.

## Project layout

evals/
Versioned golden cases and offline evaluation runner

```text
app/
  main.py                    FastAPI application and CORS
  config.py                  Environment settings
  database.py                Async SQLAlchemy setup
  models.py / schema.py      Database and API models
  api/                       Auth, documents, multimodal, monitoring
  dependencies/auth.py       JWT authentication dependency
  services/                  OCR, VLM, STT, TTS, storage, caching
streamlit_app.py             Streamlit client application
Dockerfile.api               API image
Dockerfile.ui                Streamlit image
docker-compose.yml            Pull-only runtime stack
.github/workflows/            Docker Hub and EC2 deployment workflow
tests/                        Automated tests
```

## Configuration

Create `.env` in the project root. Never commit it.

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/document_intelligence
REDIS_URL=redis://host:6379/0
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
PASSWORD_RESET_EXPIRE_MINUTES=30
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:8501

OPENAI_API_KEY=
GEMINI_API_KEY=replace-me
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TTS_MODEL=gemini-2.0-flash
GROQ_API_KEY=replace-me
GROQ_MODEL=mixtral-8x7b-32768
NVIDIA_API_KEY=replace-me
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_PRIMARY_MODEL=meta/llama-3.2-90b-vision-instruct

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=replace-me
SUPABASE_BUCKET_NAME=documents

PORTKEYS_ENABLED=false
PORTKEYS_API_KEY=
ONLINE_EVAL_ENABLED=false
ONLINE_EVAL_SAMPLE_RATE=1.0
DOCKERHUB_USERNAME=your-dockerhub-username
```

## Local development without Docker

Use the existing virtual environment or create one:

```powershell
.\doc-intell\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the API in one terminal:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

Start the UI in another:

```powershell
streamlit run streamlit_app.py
```

Open `http://localhost:8501`. API documentation is at `http://localhost:8000/docs`.

## API endpoints

| Method  | Endpoint                    | Purpose                                    |
| ------- | --------------------------- | ------------------------------------------ |
| `POST`  | `/auth/register`            | Create a user and return a JWT             |
| `POST`  | `/auth/login`               | Authenticate and return a JWT              |
| `POST`  | `/auth/forgot-password`     | Send generic recovery instructions         |
| `POST`  | `/auth/reset-password`      | Consume a one-time reset token             |
| `POST`  | `/documents/`               | OCR and structured extraction for PNG/JPEG |
| `POST`  | `/documents/vlm`            | VLM extraction for PNG/JPEG                |
| `POST`  | `/multimodal/voice-image`   | Audio plus optional image processing       |
| `GET`   | `/multimodal/conversations` | List the user's conversations              |
| `GET`   | `/health/full`              | API and Redis health                       |
| `POST`  | `/feedback`                 | Submit response feedback                   |
| `GET`   | `/feedback/review-queue`    | List pending feedback for admins           |
| `PATCH` | `/feedback/{id}/review`     | Review and resolve feedback                |

Protected endpoints require `Authorization: Bearer <token>`.

## AI evaluation and safety

Run the deterministic offline evaluator with a JSON response map:

```powershell
@'
{
  "invoice-total-001": "The invoice total is 125 dollars.",
  "uncertain-001": "The missing information is the due date."
}
'@ | Set-Content evals/responses.json
.\doc-intell\Scripts\python.exe evals/run_offline.py evals/responses.json
```

The evaluator reports a versioned pass rate and exits non-zero when the
configured threshold is not met. Production prompt or model changes should
pass this suite before rollout and then be monitored with online feedback.

Multimodal transcript and prompt content is checked for common instruction
override and credential-exfiltration attempts before the model call. These
checks are defense in depth, not a replacement for provider safety controls,
outbound network restrictions, redaction, access control, and human review.

Online LLM-as-judge evaluation is fail-open and disabled by default. Set
`ONLINE_EVAL_ENABLED=true` and configure `OPENAI_API_KEY` to sample responses.
Evaluation scores and status metadata are stored in the append-only audit log;
raw prompts and responses are not stored with evaluation records. Administrators
can inspect recent records at `/monitoring/evaluations`.

## Testing

```powershell
.\doc-intell\Scripts\python.exe -m pytest -q
```

Tests mock provider calls and do not validate live credentials. A live provider smoke test should only be run intentionally because it consumes API quota.

## Docker Hub and EC2 deployment

The local machine does not need to build Docker images. GitHub Actions builds both images on a hosted runner and pushes them to Docker Hub:

- `YOUR_USERNAME/document-intelligence-api`
- `YOUR_USERNAME/document-intelligence-ui`

Create both repositories in Docker Hub. Add these GitHub repository secrets:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
EC2_HOST
EC2_USER
EC2_SSH_KEY
```

### First-time EC2 setup

1. Launch Ubuntu 22.04 or newer. Allow SSH and the required application ports in the security group, or put the services behind an HTTPS reverse proxy.
2. Install Docker and Git:

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin git
sudo usermod -aG docker "$USER"
newgrp docker
```

3. Clone the repository into `/opt/document-intelligence` and create `/opt/document-intelligence/.env` with production values. Set `CORS_ORIGINS` to the UI's public origin and set `DOCKERHUB_USERNAME`.
4. Start the pre-built images:

```bash
cd /opt/document-intelligence
docker compose pull
docker compose up -d --no-build
docker compose ps
curl --fail http://localhost:8000/
```

### Automatic deployment

The workflow runs on pushes to `main` or manually from the Actions tab. It builds and pushes images tagged with both `latest` and the commit SHA. The EC2 step sets `IMAGE_TAG` to the commit SHA, pulls those exact images, and restarts the services with `--no-build`.

The workflow expects the repository to already exist at `/opt/document-intelligence` on EC2. It does not transfer application secrets. Keep provider credentials in the EC2 `.env` file or a secrets manager.

## Production notes

- Use RDS or another managed PostgreSQL service and ElastiCache or another managed Redis service.
- Put TLS termination and authentication-aware access controls in front of public services.
- Restrict `CORS_ORIGINS` to the actual UI origin; do not use `*` in production.
- Back up the database and configure monitoring before enabling public traffic.
- Use an Alembic migration pipeline instead of relying on startup table creation for schema changes.
